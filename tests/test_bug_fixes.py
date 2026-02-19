"""
Unit tests for the 7 bug fixes applied in the code review.
Runs without Docker or PostgreSQL — all DB/Docker calls are mocked.
"""
import sys
import types
import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch, call
import pytest

# ---------------------------------------------------------------------------
# Stub out modules that require live services so imports succeed
# ---------------------------------------------------------------------------
for mod in [
    "docker", "docker.errors", "docker.models",
    "scrapli", "napalm",
    "sqlalchemy", "sqlalchemy.orm", "sqlalchemy.dialects",
    "sqlalchemy.dialects.postgresql",
    "alembic",
    "psycopg2",
    "anthropic",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

# Make docker.errors.NotFound and DockerException importable
import docker.errors  # noqa: E402  (already mocked above)
docker.errors.NotFound = type("NotFound", (Exception,), {})
docker.errors.DockerException = type("DockerException", (Exception,), {})


# ===========================================================================
# BUG 1 — docker.py: duplicate 'labels' keyword crashes container creation
# ===========================================================================
class TestDockerLabels:
    """
    create_container() must merge caller-supplied labels with the base labels
    instead of passing two conflicting 'labels' keyword args to the Docker SDK.
    """

    def _make_runtime(self):
        with patch("docker.DockerClient") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.ping.return_value = True

            # Import here so the patched docker is used
            import importlib, importlib.util, pathlib
            spec = importlib.util.spec_from_file_location(
                "docker_mod",
                pathlib.Path(__file__).parent.parent /
                "backend/app/runtime/docker.py",
            )
            mod = importlib.util.module_from_spec(spec)

            # Patch docker inside the module namespace
            mod_docker = MagicMock()
            mod_docker.DockerClient.return_value = mock_client
            mod_docker.errors = docker.errors
            sys.modules["docker"] = mod_docker

            spec.loader.exec_module(mod)
            return mod.DockerRuntime(), mock_client

    def test_no_duplicate_labels_kwarg(self):
        runtime, mock_client = self._make_runtime()

        # Simulate what manager.py passes
        extra_labels = {
            "neon.lab_id": "lab-123",
            "neon.node_id": "node-456",
            "neon.node_name": "R1",
        }

        mock_image = MagicMock()
        mock_image.tags = ["frr:latest"]
        mock_client.images.get.return_value = mock_image
        mock_container = MagicMock()
        mock_container.id = "abc123"
        mock_client.containers.create.return_value = mock_container

        # This must NOT raise TypeError: got multiple values for 'labels'
        container_id = runtime.create_container(
            image="frr:latest",
            name="neon_test_R1",
            labels=extra_labels,
        )

        assert container_id == "abc123"
        _, kwargs = mock_client.containers.create.call_args
        final_labels = kwargs.get("labels") or mock_client.containers.create.call_args[0][0].get("labels", {})

        # Both base labels and caller labels must be present
        call_kwargs = mock_client.containers.create.call_args[1]
        passed_labels = call_kwargs.get("labels", {})
        assert passed_labels.get("neon.managed") == "true", "Base label missing"
        assert passed_labels.get("neon.lab_id") == "lab-123", "Caller label missing"
        assert "neon.node_name" in passed_labels, "Caller label missing"


# ===========================================================================
# BUG 2 — images.py: /vendors/ unreachable when defined after /{image_id}
# ===========================================================================
class TestImageRouteOrdering:
    """
    GET /vendors/ must be registered BEFORE GET /{image_id} so FastAPI
    doesn't try to parse the string 'vendors' as a UUID.
    """

    def _load_router(self):
        import importlib.util, pathlib
        # Stub app dependencies
        for m in ["app", "app.db", "app.db.base", "app.db.models",
                  "app.core", "app.core.config"]:
            sys.modules.setdefault(m, MagicMock())

        spec = importlib.util.spec_from_file_location(
            "images_mod",
            pathlib.Path(__file__).parent.parent /
            "backend/app/api/v1/images.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.router

    def test_vendors_route_before_image_id(self):
        router = self._load_router()
        paths = [route.path for route in router.routes]
        assert "/vendors/" in paths, "/vendors/ route not registered"
        assert "/{image_id}" in paths, "/{image_id} route not registered"

        vendors_idx = paths.index("/vendors/")
        image_id_idx = paths.index("/{image_id}")
        assert vendors_idx < image_id_idx, (
            f"/vendors/ (idx {vendors_idx}) must come before "
            f"/{{image_id}} (idx {image_id_idx})"
        )


# ===========================================================================
# BUG 4 — topology_builder.py: stale lab.links → duplicate interface names
# ===========================================================================
class TestInterfaceAutoAssignment:
    """
    When add_links() creates multiple links in one call, each successive link
    must get a distinct interface name even though lab.links is a stale
    SQLAlchemy collection that is not refreshed between flushes.
    """

    def _load_builder(self):
        import importlib.util, pathlib
        for m in ["app", "app.db", "app.db.base", "app.db.models",
                  "app.core", "app.core.config"]:
            sys.modules.setdefault(m, MagicMock())

        # Build lightweight stub models
        class StubNode:
            def __init__(self, name, node_id=None):
                self.name = name
                self.id = node_id or uuid.uuid4()

        class StubLink:
            def __init__(self, src_id, src_iface, tgt_id, tgt_iface):
                self.source_node_id = src_id
                self.source_interface = src_iface
                self.target_node_id = tgt_id
                self.target_interface = tgt_iface

        class StubLab:
            def __init__(self, nodes, links):
                self.nodes = nodes
                self.links = links  # static — never updated (intentionally stale)

        # Patch the models inside the module
        stub_models = MagicMock()
        nodes = [StubNode(f"R{i+1}") for i in range(4)]

        created_links = []

        class FakeLink:
            def __init__(self, **kw):
                self.id = uuid.uuid4()
                for k, v in kw.items():
                    setattr(self, k, v)

        stub_models.Link = FakeLink
        stub_models.Lab = MagicMock()
        stub_models.Node = MagicMock()
        stub_models.Image = MagicMock()
        sys.modules["app.db.models"] = stub_models

        spec = importlib.util.spec_from_file_location(
            "topo_builder",
            pathlib.Path(__file__).parent.parent /
            "backend/app/services/topology_builder.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.TopologyBuilder, StubNode, StubLab

    def test_unique_interfaces_in_batch(self):
        Builder, StubNode, StubLab = self._load_builder()
        builder = Builder()

        r1 = StubNode("R1")
        r2 = StubNode("R2")
        r3 = StubNode("R3")

        # Lab starts with NO existing links — but the collection is static
        lab = StubLab(nodes=[r1, r2, r3], links=[])

        db = MagicMock()
        # Make db.query(Lab).filter().first() return our stub lab
        db.query.return_value.filter.return_value.first.return_value = lab

        link_specs = [
            {"source": "R1", "target": "R2"},  # R1→eth0, R2→eth0
            {"source": "R1", "target": "R3"},  # R1→eth1 (not eth0 again!), R3→eth0
        ]

        result = builder.add_links(lab_id=uuid.uuid4(), links=link_specs, db=db)

        assert len(result) == 2

        # Parse assignments from the result strings "node:iface"
        r1_ifaces = [
            r.split(":")[1] for r in
            [result[0]["source"], result[1]["source"]]
        ]
        # R1 is source in both links → must have two DIFFERENT interfaces
        assert r1_ifaces[0] != r1_ifaces[1], (
            f"R1 was assigned the same interface twice: {r1_ifaces}"
        )

    def test_existing_links_respected(self):
        """Interfaces already in use must be skipped."""
        Builder, StubNode, StubLab = self._load_builder()
        builder = Builder()

        r1 = StubNode("R1")
        r2 = StubNode("R2")
        r3 = StubNode("R3")

        class ExistingLink:
            source_node_id = r1.id
            source_interface = "eth0"
            target_node_id = r2.id
            target_interface = "eth0"

        lab = StubLab(nodes=[r1, r2, r3], links=[ExistingLink()])

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = lab

        # Add another link from R1 — must skip eth0
        result = builder.add_links(
            lab_id=uuid.uuid4(),
            links=[{"source": "R1", "target": "R3"}],
            db=db,
        )

        r1_iface = result[0]["source"].split(":")[1]
        assert r1_iface != "eth0", (
            f"R1 should have skipped eth0 (already used) but got: {r1_iface}"
        )


# ===========================================================================
# BUG 5 — topology_builder.py: redundant join+has() in vendor filter
# ===========================================================================
class TestVendorFilter:
    """
    The vendor filter must NOT call .join() — only .filter(Image.vendor.has()).
    A spurious .join() can produce ambiguous SQL with some SQLAlchemy versions.
    """

    def test_no_spurious_join_in_vendor_filter(self):
        import ast, pathlib
        src = (
            pathlib.Path(__file__).parent.parent /
            "backend/app/services/topology_builder.py"
        ).read_text()
        tree = ast.parse(src)

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name != "add_nodes":
                continue
            func_src = ast.get_source_segment(src, node)
            # The vendor-filter block must NOT contain .join(Image.vendor)
            assert "join(Image.vendor)" not in func_src, (
                "Redundant .join(Image.vendor) still present in add_nodes"
            )


# ===========================================================================
# BUG 6 — topology_builder.py: count type Union[int, Dict] for spine-leaf
# ===========================================================================
class TestSpineLeafTypeGuard:
    """
    create_topology_pattern() must raise ValueError with a clear message when
    the wrong count type is passed for a pattern.
    """

    def _load_builder(self):
        import importlib.util, pathlib
        for m in ["app", "app.db", "app.db.base", "app.db.models",
                  "app.core", "app.core.config"]:
            sys.modules.setdefault(m, MagicMock())
        sys.modules["app.db.models"] = MagicMock()

        spec = importlib.util.spec_from_file_location(
            "topo_builder2",
            pathlib.Path(__file__).parent.parent /
            "backend/app/services/topology_builder.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.TopologyBuilder

    def test_spine_leaf_requires_dict(self):
        Builder = self._load_builder()
        builder = Builder()
        with pytest.raises(ValueError, match="dict"):
            builder.create_topology_pattern(
                lab_id=uuid.uuid4(),
                pattern="spine-leaf",
                count=4,        # wrong — should be dict
                image_type="switch",
                db=MagicMock(),
            )

    def test_ring_requires_int(self):
        Builder = self._load_builder()
        builder = Builder()
        with pytest.raises(ValueError, match="int"):
            builder.create_topology_pattern(
                lab_id=uuid.uuid4(),
                pattern="ring",
                count={"spines": 2},   # wrong — should be int
                image_type="router",
                db=MagicMock(),
            )


# ===========================================================================
# BUG 7 — network.py: conflicting root tc qdiscs
# ===========================================================================
class TestTcQdiscs:
    """
    When BOTH bandwidth and delay_ms are specified, _apply_tc must use a
    chained tbf→netem hierarchy (two separate tc calls) rather than two
    root qdiscs (which would fail with EEXIST on Linux).
    """

    def _load_network(self):
        import importlib.util, pathlib
        sys.modules["docker"] = MagicMock()

        spec = importlib.util.spec_from_file_location(
            "net_mod",
            pathlib.Path(__file__).parent.parent /
            "backend/app/runtime/network.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.NetworkManager

    def _get_tc_calls(self, run_mock):
        """Extract the tc sub-commands from subprocess.run calls."""
        tc_cmds = []
        for c in run_mock.call_args_list:
            args = c[0][0]
            if "tc" in args:
                tc_cmds.append(args)
        return tc_cmds

    def test_bandwidth_only_single_root_qdisc(self):
        NM = self._load_network()
        nm = NM.__new__(NM)
        nm.client = MagicMock()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            nm._apply_tc(pid=1234, interface="eth1", bandwidth="1gbit")

        tc_cmds = self._get_tc_calls(mock_run)
        roots = [c for c in tc_cmds if "root" in c and "tbf" in c]
        assert len(roots) == 1, "Expected exactly one root tbf qdisc"
        parents = [c for c in tc_cmds if "parent" in c]
        assert len(parents) == 0, "Should be no child qdiscs for bandwidth-only"

    def test_delay_only_single_root_qdisc(self):
        NM = self._load_network()
        nm = NM.__new__(NM)
        nm.client = MagicMock()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            nm._apply_tc(pid=1234, interface="eth1", delay_ms=50)

        tc_cmds = self._get_tc_calls(mock_run)
        roots = [c for c in tc_cmds if "root" in c and "netem" in c]
        assert len(roots) == 1, "Expected exactly one root netem qdisc"

    def test_bandwidth_and_delay_uses_chained_qdiscs(self):
        NM = self._load_network()
        nm = NM.__new__(NM)
        nm.client = MagicMock()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            nm._apply_tc(pid=1234, interface="eth1", bandwidth="1gbit", delay_ms=20)

        tc_cmds = self._get_tc_calls(mock_run)

        # Must have exactly 2 tc calls: one for tbf root, one for netem child
        assert len(tc_cmds) == 2, (
            f"Expected 2 tc calls (tbf+netem chain), got {len(tc_cmds)}: {tc_cmds}"
        )

        tbf_call = tc_cmds[0]
        netem_call = tc_cmds[1]

        # First call: root tbf
        assert "root" in tbf_call and "tbf" in tbf_call, \
            f"First call should be root tbf: {tbf_call}"
        assert "parent" not in tbf_call, \
            "tbf should be root, not a child"

        # Second call: child netem (NOT root)
        assert "netem" in netem_call, \
            f"Second call should be netem: {netem_call}"
        assert "parent" in netem_call, \
            "netem must be chained as a child, not a second root"
        assert "root" not in netem_call or netem_call.index("root") > netem_call.index("parent"), \
            "netem should use 'parent', not 'root'"

    def test_bandwidth_and_loss_uses_chained_qdiscs(self):
        NM = self._load_network()
        nm = NM.__new__(NM)
        nm.client = MagicMock()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            nm._apply_tc(pid=1234, interface="eth1", bandwidth="100mbit", loss_percent=1.5)

        tc_cmds = self._get_tc_calls(mock_run)
        assert len(tc_cmds) == 2, \
            f"Expected 2 tc calls for bandwidth+loss, got {len(tc_cmds)}"
        assert "parent" in tc_cmds[1], "netem must be a child qdisc"
