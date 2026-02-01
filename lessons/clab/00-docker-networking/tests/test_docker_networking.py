"""
Lesson 0: Docker Networking - Validation Tests

Run with: pytest tests/test_docker_networking.py -v
"""

import subprocess
import json
import pytest


def run_docker(cmd: str) -> str:
    """Run a docker command and return output."""
    result = subprocess.run(
        f"docker {cmd}",
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


def docker_exists(name: str) -> bool:
    """Check if a container exists."""
    result = run_docker(f"ps -a --filter name={name} --format '{{{{.Names}}}}'")
    return name in result


def network_exists(name: str) -> bool:
    """Check if a network exists."""
    result = run_docker(f"network ls --filter name={name} --format '{{{{.Name}}}}'")
    return name in result


class TestDockerBasics:
    """Verify Docker is working correctly."""

    def test_docker_available(self):
        """Docker CLI should be available."""
        result = subprocess.run(
            "docker --version",
            shell=True,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "Docker version" in result.stdout

    def test_docker_running(self):
        """Docker daemon should be running."""
        result = subprocess.run(
            "docker info",
            shell=True,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0


class TestDefaultBridge:
    """Test understanding of default bridge network."""

    def test_default_bridge_exists(self):
        """Default bridge network should exist."""
        assert network_exists("bridge")

    def test_default_bridge_subnet(self):
        """Default bridge should have expected subnet."""
        result = run_docker("network inspect bridge --format '{{.IPAM.Config}}'")
        # Should contain a 172.17.x.x subnet typically
        assert "172." in result or "Subnet" in result


class TestCustomNetwork:
    """Test custom network creation."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Create and cleanup test network."""
        run_docker("network create test-validation-net 2>/dev/null || true")
        yield
        run_docker("network rm test-validation-net 2>/dev/null || true")

    def test_can_create_network(self):
        """Should be able to create custom network."""
        assert network_exists("test-validation-net")

    def test_custom_network_has_driver(self):
        """Custom network should use bridge driver."""
        result = run_docker(
            "network inspect test-validation-net --format '{{.Driver}}'"
        )
        assert result == "bridge"


class TestNetworkCommunication:
    """Test container communication scenarios."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Create test environment."""
        # Create network
        run_docker("network create comm-test-net 2>/dev/null || true")

        # Create containers
        run_docker(
            "run -d --name comm-test-1 --network comm-test-net "
            "alpine sleep 300 2>/dev/null || true"
        )
        run_docker(
            "run -d --name comm-test-2 --network comm-test-net "
            "alpine sleep 300 2>/dev/null || true"
        )

        yield

        # Cleanup
        run_docker("rm -f comm-test-1 comm-test-2 2>/dev/null || true")
        run_docker("network rm comm-test-net 2>/dev/null || true")

    def test_containers_can_ping_by_name(self):
        """Containers on custom network should resolve names."""
        result = subprocess.run(
            "docker exec comm-test-1 ping -c 1 comm-test-2",
            shell=True,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "1 packets transmitted, 1 packets received" in result.stdout \
            or "1 received" in result.stdout


class TestMultipleNetworks:
    """Test multi-network scenarios."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Create multi-network test environment."""
        run_docker("network create multi-net-1 2>/dev/null || true")
        run_docker("network create multi-net-2 2>/dev/null || true")
        run_docker(
            "run -d --name multi-test-container --network multi-net-1 "
            "alpine sleep 300 2>/dev/null || true"
        )

        yield

        run_docker("rm -f multi-test-container 2>/dev/null || true")
        run_docker("network rm multi-net-1 multi-net-2 2>/dev/null || true")

    def test_can_connect_to_additional_network(self):
        """Container should be able to join multiple networks."""
        # Connect to second network
        run_docker("network connect multi-net-2 multi-test-container")

        # Inspect container networks
        result = run_docker(
            "inspect multi-test-container "
            "--format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}'"
        )

        assert "multi-net-1" in result
        assert "multi-net-2" in result


class TestNetworkIsolation:
    """Test that network isolation works correctly."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Create isolated network test environment."""
        run_docker("network create iso-net-1 2>/dev/null || true")
        run_docker("network create iso-net-2 2>/dev/null || true")
        run_docker(
            "run -d --name iso-container-1 --network iso-net-1 "
            "alpine sleep 300 2>/dev/null || true"
        )
        run_docker(
            "run -d --name iso-container-2 --network iso-net-2 "
            "alpine sleep 300 2>/dev/null || true"
        )

        yield

        run_docker("rm -f iso-container-1 iso-container-2 2>/dev/null || true")
        run_docker("network rm iso-net-1 iso-net-2 2>/dev/null || true")

    def test_containers_on_different_networks_isolated(self):
        """Containers on different networks should not communicate."""
        # Get IP of container-2
        ip = run_docker(
            "inspect iso-container-2 "
            "--format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'"
        )

        # Try to ping (should fail)
        result = subprocess.run(
            f"docker exec iso-container-1 ping -c 1 -W 2 {ip}",
            shell=True,
            capture_output=True,
            text=True
        )

        # Should timeout or have 100% packet loss
        assert result.returncode != 0 or "100% packet loss" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
