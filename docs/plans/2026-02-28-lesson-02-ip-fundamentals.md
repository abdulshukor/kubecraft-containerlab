# Lesson 02: IP Fundamentals & Basic Connectivity -- Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create lesson 02 teaching IP addressing fundamentals, OSI layers 1-4, and Ansible with Jinja2 templates, using a 4-node containerlab topology.

**Architecture:** A `host1--srl1--srl2--host2` topology with three subnets. Linux hosts get IPs via containerlab `exec`. SR Linux routers are configured via Ansible using Jinja2 templates that generate CLI commands pushed over JSON-RPC. Adjacent pings work; cross-subnet fails (teaser for lesson 03 routing).

**Tech Stack:** Containerlab, Nokia SR Linux 24.10.1, Alpine Linux, Ansible (builtin `uri` module), Jinja2 templates, pytest

**Design doc:** `docs/plans/2026-02-28-lesson-02-ip-fundamentals-design.md`

---

## IP Addressing Scheme

| Subnet | Link | Left Device | Right Device |
|--------|------|-------------|--------------|
| `10.1.1.0/24` | host1 -- srl1 | host1: `eth1` = `10.1.1.2` | srl1: `e1-1` = `10.1.1.1` |
| `10.1.2.0/24` | srl1 -- srl2 | srl1: `e1-2` = `10.1.2.1` | srl2: `e1-1` = `10.1.2.2` |
| `10.1.3.0/24` | srl2 -- host2 | srl2: `e1-2` = `10.1.3.1` | host2: `eth1` = `10.1.3.2` |

Management IPs (pinned in topology):
- srl1: `172.20.20.11`
- srl2: `172.20.20.12`

SR Linux credentials: `admin` / `NokiaSrl1!`

---

### Task 1: Create directory structure and topology file

**Files:**
- Create: `lessons/clab/02-ip-fundamentals/topology/lab.clab.yml`

**Step 1: Create directory structure**

```bash
mkdir -p lessons/clab/02-ip-fundamentals/{topology,ansible/{templates,host_vars},exercises,solutions,tests}
```

**Step 2: Write the topology file**

Create `lessons/clab/02-ip-fundamentals/topology/lab.clab.yml`:

```yaml
# Lesson 2: IP Fundamentals -- 4-Node Linear Topology
# host1 -- srl1 -- srl2 -- host2

name: ip-fundamentals

topology:
  nodes:
    srl1:
      kind: srl
      image: ghcr.io/nokia/srlinux:24.10.1
      mgmt-ipv4: 172.20.20.11

    srl2:
      kind: srl
      image: ghcr.io/nokia/srlinux:24.10.1
      mgmt-ipv4: 172.20.20.12

    host1:
      kind: linux
      image: alpine:3.20
      exec:
        - ip link set eth1 up
        - ip addr add 10.1.1.2/24 dev eth1
        - ip route add default via 10.1.1.1 dev eth1

    host2:
      kind: linux
      image: alpine:3.20
      exec:
        - ip link set eth1 up
        - ip addr add 10.1.3.2/24 dev eth1
        - ip route add default via 10.1.3.1 dev eth1

  links:
    - endpoints: ["host1:eth1", "srl1:e1-1"]
    - endpoints: ["srl1:e1-2", "srl2:e1-1"]
    - endpoints: ["srl2:e1-2", "host2:eth1"]
```

**Step 3: Verify YAML is valid**

```bash
python3 -c "import yaml; yaml.safe_load(open('lessons/clab/02-ip-fundamentals/topology/lab.clab.yml'))" && echo "Valid YAML"
```

Expected: `Valid YAML`

**Step 4: Commit**

```bash
git add lessons/clab/02-ip-fundamentals/topology/lab.clab.yml
git commit -m "feat(lesson-02): add 4-node linear topology file"
```

---

### Task 2: Create Ansible configuration

**Files:**
- Create: `lessons/clab/02-ip-fundamentals/ansible/inventory.yml`
- Create: `lessons/clab/02-ip-fundamentals/ansible/host_vars/srl1.yml`
- Create: `lessons/clab/02-ip-fundamentals/ansible/host_vars/srl2.yml`
- Create: `lessons/clab/02-ip-fundamentals/ansible/templates/srl_interfaces.json.j2`
- Create: `lessons/clab/02-ip-fundamentals/ansible/playbook.yml`

**Step 1: Write the inventory file**

Create `lessons/clab/02-ip-fundamentals/ansible/inventory.yml`:

```yaml
---
all:
  children:
    routers:
      hosts:
        srl1:
          ansible_host: 172.20.20.11
        srl2:
          ansible_host: 172.20.20.12
```

**Step 2: Write host_vars for srl1**

Create `lessons/clab/02-ip-fundamentals/ansible/host_vars/srl1.yml`:

```yaml
---
interfaces:
  - name: ethernet-1/1
    ipv4_address: 10.1.1.1/24
    description: Link to host1
  - name: ethernet-1/2
    ipv4_address: 10.1.2.1/24
    description: Link to srl2
```

**Step 3: Write host_vars for srl2**

Create `lessons/clab/02-ip-fundamentals/ansible/host_vars/srl2.yml`:

```yaml
---
interfaces:
  - name: ethernet-1/1
    ipv4_address: 10.1.2.2/24
    description: Link to srl1
  - name: ethernet-1/2
    ipv4_address: 10.1.3.1/24
    description: Link to host2
```

**Step 4: Write the Jinja2 template**

Create `lessons/clab/02-ip-fundamentals/ansible/templates/srl_interfaces.json.j2`:

```jinja2
{# Generates SR Linux CLI commands for interface configuration.
   Variables come from host_vars/<hostname>.yml:
     interfaces:
       - name: ethernet-1/1
         ipv4_address: 10.1.1.1/24
         description: Link to host1
#}
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "cli",
  "params": {
    "commands": [
      "enter candidate",
{% for iface in interfaces %}
      "set / interface {{ iface.name }} admin-state enable",
      "set / interface {{ iface.name }} subinterface 0 admin-state enable",
      "set / interface {{ iface.name }} subinterface 0 description {{ iface.description }}",
      "set / interface {{ iface.name }} subinterface 0 ipv4 admin-state enable",
      "set / interface {{ iface.name }} subinterface 0 ipv4 address {{ iface.ipv4_address }}",
      "set / network-instance default interface {{ iface.name }}.0",
{% endfor %}
      "commit now"
    ]
  }
}
```

**Step 5: Write the playbook**

Create `lessons/clab/02-ip-fundamentals/ansible/playbook.yml`:

```yaml
---
# Lesson 2: Configure IP addresses on SR Linux routers
#
# This playbook uses a Jinja2 template to generate SR Linux CLI commands
# and pushes them via the JSON-RPC API. Each router gets its own set of
# commands based on its host_vars (ansible/host_vars/<hostname>.yml).
#
# Usage:
#   ansible-playbook -i inventory.yml playbook.yml

- name: Configure SR Linux router interfaces
  hosts: routers
  gather_facts: false
  connection: local

  tasks:
    - name: Apply interface configuration via JSON-RPC
      ansible.builtin.uri:
        url: "http://{{ ansible_host }}/jsonrpc"
        method: POST
        url_username: admin
        url_password: NokiaSrl1!
        force_basic_auth: true
        body_format: json
        body: "{{ lookup('template', 'templates/srl_interfaces.json.j2') }}"
        status_code: 200
      register: config_result

    - name: Show configuration result
      ansible.builtin.debug:
        msg: "{{ inventory_hostname }}: Configuration applied successfully"
      when: config_result.status == 200

    - name: Verify interfaces are configured
      ansible.builtin.uri:
        url: "http://{{ ansible_host }}/jsonrpc"
        method: POST
        url_username: admin
        url_password: NokiaSrl1!
        force_basic_auth: true
        body_format: json
        body:
          jsonrpc: "2.0"
          id: 2
          method: get
          params:
            commands:
              - path: /network-instance[name=default]/interface
                datastore: state
        status_code: 200
      register: verify_result

    - name: Display configured interfaces
      ansible.builtin.debug:
        msg: "{{ inventory_hostname }} interfaces: {{ verify_result.json.result | default('check manually') }}"
```

**Step 6: Verify YAML validity of all Ansible files**

```bash
python3 -c "
import yaml, pathlib
for f in pathlib.Path('lessons/clab/02-ip-fundamentals/ansible').rglob('*.yml'):
    yaml.safe_load(f.read_text())
    print(f'OK: {f}')
"
```

Expected: all files show `OK`

**Step 7: Commit**

```bash
git add lessons/clab/02-ip-fundamentals/ansible/
git commit -m "feat(lesson-02): add Ansible playbook with Jinja2 templates for SR Linux config"
```

---

### Task 3: Write README.md

**Files:**
- Create: `lessons/clab/02-ip-fundamentals/README.md`

**Step 1: Write the lesson README**

Create `lessons/clab/02-ip-fundamentals/README.md` following the exact structure from lesson 01's README. Content sections:

1. Title and one-line description
2. Objectives (checkboxes)
3. Prerequisites
4. Video Outline sections:
   - Section 1: The Networking Stack -- OSI Layers 1-4 (3 min)
     - Map each layer to lesson 00 primitives: L1=veth pairs, L2=MAC/bridges, L3=IP/subnets, L4=TCP/UDP ports
   - Section 2: IP Addressing Fundamentals (3 min)
     - CIDR notation, subnet masks, "are these two IPs on the same network?" test
     - ARP: how L3 addresses resolve to L2 addresses
   - Section 3: Ansible 101 (3 min)
     - Why automate? (consistency, repeatability, version control)
     - Inventory: which devices to manage
     - Host vars: per-device data
     - Jinja2 templates: one template + different variables = different configs
     - Playbook: the orchestration glue
   - Section 4: Live Demo -- Deploy and Configure (3 min)
     - Deploy topology, run playbook, verify with ping
   - Section 5: Verification Commands (1 min)
     - ping, ip addr, ARP tables, SR Linux equivalents
   - Section 6: Recap + Teaser (30s)
5. Lab Topology (Mermaid diagram)
6. IP Addressing Table
7. Files in This Lesson (directory tree)
8. Key Commands Reference table
9. Link to exercises
10. Common Issues section
11. What's Next (link to lesson 03)
12. Additional Resources

**Step 2: Commit**

```bash
git add lessons/clab/02-ip-fundamentals/README.md
git commit -m "feat(lesson-02): add lesson README with OSI/IP/Ansible overview"
```

---

### Task 4: Write exercises and solutions

**Files:**
- Create: `lessons/clab/02-ip-fundamentals/exercises/README.md`
- Create: `lessons/clab/02-ip-fundamentals/solutions/README.md`

**Step 1: Write exercises**

Create `lessons/clab/02-ip-fundamentals/exercises/README.md` with 6 exercises:

**Exercise 1: Deploy and Verify**
- Deploy topology: `containerlab deploy -t topology/lab.clab.yml`
- Run Ansible playbook: `cd ansible && ansible-playbook -i inventory.yml playbook.yml`
- Verify adjacent connectivity:
  - `docker exec clab-ip-fundamentals-host1 ping -c 3 10.1.1.1` (host1 -> srl1)
  - `docker exec clab-ip-fundamentals-host2 ping -c 3 10.1.3.1` (host2 -> srl2)
  - Connect to srl1: `docker exec -it clab-ip-fundamentals-srl1 sr_cli`
  - From srl1: `ping 10.1.2.2 network-instance default` (srl1 -> srl2)
- Try cross-subnet: `docker exec clab-ip-fundamentals-host1 ping -c 3 10.1.3.2`
- Expected: cross-subnet ping fails (no routes on routers)
- Deliverable: note which pings succeed and which fail, explain why

**Exercise 2: Read the Config**
- Open `ansible/templates/srl_interfaces.json.j2` and `ansible/host_vars/srl2.yml`
- Manually trace through the template with srl2's variables
- Write out the exact CLI commands that will be generated for srl2
- Deliverable: file `exercises/srl2-commands.txt` with the generated commands

**Exercise 3: Add a Loopback Interface**
- Add a loopback interface to srl1's host_vars:
  ```yaml
  - name: lo0
    ipv4_address: 10.10.10.1/32
    description: Loopback for management
  ```
- Update the Jinja2 template if needed (hint: the template should already handle it via the loop)
- Re-run the playbook
- Verify: `docker exec -it clab-ip-fundamentals-srl1 sr_cli -c "show interface lo0"`
- Deliverable: modified `host_vars/srl1.yml`

**Exercise 4: Break/Fix -- Interface Down**
- Scenario: admin-disable srl1's ethernet-1/1
  ```
  docker exec -it clab-ip-fundamentals-srl1 sr_cli
  enter candidate
  set / interface ethernet-1/1 admin-state disable
  commit now
  ```
- Symptom: host1 can no longer ping srl1
- Task: diagnose using `show interface brief`, identify the admin-down interface, fix it
- Deliverable: document the diagnostic commands used and the fix

**Exercise 5: Break/Fix -- Subnet Mismatch**
- Scenario: change host1's IP to a different subnet
  ```bash
  docker exec clab-ip-fundamentals-host1 ip addr del 10.1.1.2/24 dev eth1
  docker exec clab-ip-fundamentals-host1 ip addr add 10.1.1.2/30 dev eth1
  ```
- Symptom: host1 can't ping srl1 (10.1.1.1)
- Task: diagnose using `ip addr show eth1` on host1 and `show interface ethernet-1/1 detail` on srl1
- Hint: check the subnet masks -- /30 means only .0-.3 are in the subnet
- Deliverable: explain why /30 breaks connectivity and how to fix it

**Exercise 6: Break/Fix -- Missing Gateway**
- Scenario: remove host1's default route
  ```bash
  docker exec clab-ip-fundamentals-host1 ip route del default
  ```
- Symptom: host1 can ping srl1 (10.1.1.1) but not srl2 (10.1.2.1)
- Task: diagnose using `ip route show`, understand why local subnet works but remote doesn't
- Deliverable: explain the difference between local and remote subnets, restore the route

**Step 2: Write solutions**

Create `lessons/clab/02-ip-fundamentals/solutions/README.md` with solutions for all 6 exercises. Include:
- Exact commands and expected output
- Explanations of why things work/fail
- Key takeaways per exercise

**Step 3: Commit**

```bash
git add lessons/clab/02-ip-fundamentals/exercises/ lessons/clab/02-ip-fundamentals/solutions/
git commit -m "feat(lesson-02): add exercises with break/fix scenarios and solutions"
```

---

### Task 5: Write tests

**Files:**
- Create: `lessons/clab/02-ip-fundamentals/tests/test_ip_fundamentals.py`

**Step 1: Write the test file**

Create `lessons/clab/02-ip-fundamentals/tests/test_ip_fundamentals.py` following the pattern from lesson 01's `test_lab.py`. Test classes:

```python
"""
Lesson 2: IP Fundamentals -- Validation Tests

Run with: pytest tests/test_ip_fundamentals.py -v
"""

import subprocess
import os
import pytest
from pathlib import Path

LESSON_DIR = Path(__file__).parent.parent
TOPOLOGY_FILE = LESSON_DIR / "topology" / "lab.clab.yml"
ANSIBLE_DIR = LESSON_DIR / "ansible"


def run_command(cmd: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    return subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=timeout
    )


class TestEnvironment:
    """Verify the lab environment is correctly set up."""

    def test_containerlab_installed(self):
        result = run_command("containerlab version")
        assert result.returncode == 0

    def test_docker_available(self):
        result = run_command("docker version")
        assert result.returncode == 0

    def test_ansible_installed(self):
        result = run_command("ansible --version")
        assert result.returncode == 0

    def test_topology_file_exists(self):
        assert TOPOLOGY_FILE.exists()

    def test_topology_file_valid_yaml(self):
        import yaml
        with open(TOPOLOGY_FILE) as f:
            data = yaml.safe_load(f)
            assert data is not None
            assert "topology" in data


class TestTopologyStructure:
    """Verify topology file has correct structure."""

    @pytest.fixture
    def topology(self):
        import yaml
        with open(TOPOLOGY_FILE) as f:
            return yaml.safe_load(f)

    def test_has_four_nodes(self, topology):
        nodes = topology["topology"]["nodes"]
        assert len(nodes) == 4

    def test_has_srl_nodes(self, topology):
        nodes = topology["topology"]["nodes"]
        assert "srl1" in nodes
        assert "srl2" in nodes
        assert nodes["srl1"]["kind"] == "srl"
        assert nodes["srl2"]["kind"] == "srl"

    def test_has_linux_hosts(self, topology):
        nodes = topology["topology"]["nodes"]
        assert "host1" in nodes
        assert "host2" in nodes
        assert nodes["host1"]["kind"] == "linux"
        assert nodes["host2"]["kind"] == "linux"

    def test_has_three_links(self, topology):
        links = topology["topology"]["links"]
        assert len(links) == 3

    def test_no_latest_tags(self, topology):
        nodes = topology["topology"]["nodes"]
        for name, config in nodes.items():
            image = config.get("image", "")
            assert "latest" not in image, f"Node {name} uses 'latest' tag"


class TestAnsibleStructure:
    """Verify Ansible configuration files exist and are valid."""

    def test_inventory_exists(self):
        assert (ANSIBLE_DIR / "inventory.yml").exists()

    def test_playbook_exists(self):
        assert (ANSIBLE_DIR / "playbook.yml").exists()

    def test_template_exists(self):
        assert (ANSIBLE_DIR / "templates" / "srl_interfaces.json.j2").exists()

    def test_host_vars_exist(self):
        assert (ANSIBLE_DIR / "host_vars" / "srl1.yml").exists()
        assert (ANSIBLE_DIR / "host_vars" / "srl2.yml").exists()

    def test_inventory_valid_yaml(self):
        import yaml
        with open(ANSIBLE_DIR / "inventory.yml") as f:
            data = yaml.safe_load(f)
            assert "all" in data

    def test_host_vars_have_interfaces(self):
        import yaml
        for host in ["srl1", "srl2"]:
            with open(ANSIBLE_DIR / "host_vars" / f"{host}.yml") as f:
                data = yaml.safe_load(f)
                assert "interfaces" in data
                assert len(data["interfaces"]) >= 2

    def test_template_has_jinja2_syntax(self):
        template = (ANSIBLE_DIR / "templates" / "srl_interfaces.json.j2").read_text()
        assert "{% for" in template
        assert "{{ iface" in template


class TestLabDeployment:
    """Test that the lab can be deployed. Requires containerlab + Docker."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        yield
        run_command(f"containerlab destroy -t {TOPOLOGY_FILE} --cleanup 2>/dev/null || true")

    def test_lab_deploys_successfully(self):
        run_command(f"containerlab destroy -t {TOPOLOGY_FILE} --cleanup 2>/dev/null || true")
        result = run_command(f"containerlab deploy -t {TOPOLOGY_FILE}", timeout=180)
        assert result.returncode == 0

    def test_all_containers_running(self):
        run_command(f"containerlab destroy -t {TOPOLOGY_FILE} --cleanup 2>/dev/null || true")
        run_command(f"containerlab deploy -t {TOPOLOGY_FILE}", timeout=180)
        import time; time.sleep(5)
        result = run_command("docker ps --filter 'name=clab-ip-fundamentals' --format '{{.Names}}'")
        containers = [c for c in result.stdout.strip().split('\n') if c]
        assert len(containers) == 4


class TestConnectivity:
    """Test connectivity after Ansible config is applied. Requires running lab."""

    @pytest.fixture(autouse=True)
    def deploy_and_configure(self):
        run_command(f"containerlab destroy -t {TOPOLOGY_FILE} --cleanup 2>/dev/null || true")
        run_command(f"containerlab deploy -t {TOPOLOGY_FILE}", timeout=180)
        import time; time.sleep(10)
        run_command(
            f"cd {ANSIBLE_DIR} && ansible-playbook -i inventory.yml playbook.yml",
            timeout=120
        )
        time.sleep(5)
        yield
        run_command(f"containerlab destroy -t {TOPOLOGY_FILE} --cleanup 2>/dev/null || true")

    def test_host1_pings_srl1(self):
        result = run_command("docker exec clab-ip-fundamentals-host1 ping -c 2 -W 3 10.1.1.1")
        assert result.returncode == 0

    def test_host2_pings_srl2(self):
        result = run_command("docker exec clab-ip-fundamentals-host2 ping -c 2 -W 3 10.1.3.1")
        assert result.returncode == 0

    def test_srl1_pings_srl2(self):
        result = run_command(
            "docker exec clab-ip-fundamentals-srl1 sr_cli -c 'ping -c 2 10.1.2.2 network-instance default'"
        )
        assert "2 received" in result.stdout or result.returncode == 0
```

**Step 2: Verify test file syntax**

```bash
python3 -c "import ast; ast.parse(open('lessons/clab/02-ip-fundamentals/tests/test_ip_fundamentals.py').read()); print('Syntax OK')"
```

**Step 3: Commit**

```bash
git add lessons/clab/02-ip-fundamentals/tests/
git commit -m "feat(lesson-02): add pytest validation tests"
```

---

### Task 6: Write video script

**Files:**
- Create: `lessons/clab/02-ip-fundamentals/script.md`

**Step 1: Write the video script**

Create `lessons/clab/02-ip-fundamentals/script.md` following the `VIDEO_SCRIPT_TEMPLATE.md` format. Sections:

**Lesson Information table:** Lesson 02, IP Fundamentals & Basic Connectivity, 12-15 min target

**Pre-Recording Checklist** (same pattern as lesson 01 plus Ansible check)

**Opening Hook (30s):**
> "Your app returns 'connection refused.' Is it a network problem or an application problem? After this lesson, you'll know exactly how to tell -- because you'll understand what IP addresses actually are, how devices find each other, and how to automate network configuration."

**Section 1: The Networking Stack -- Layers 1-4 (3 min):**
- Draw/show the 4 layers, map each to lesson 00 primitives:
  - L1 Physical: veth pairs -- the virtual "cable" between containers
  - L2 Data Link: MAC addresses, docker0 bridge -- "which device on this wire?"
  - L3 Network: IP addresses, subnets -- "which network? which host?"
  - L4 Transport: TCP/UDP ports -- "which application?"
- Key insight: "When you troubleshoot, work bottom-up. Is the cable connected? Can you see the MAC? Can you reach the IP? Is the port open?"

**Section 2: IP Addressing & Subnets (3 min):**
- IP addresses: network part + host part
- Subnet masks and CIDR: /24 = 256 addresses, /30 = 4 addresses
- "Same network?" test: if two IPs share the same network portion, they can communicate directly (L2). Otherwise, they need a router (L3).
- ARP: "I know the IP, but I need the MAC to send the frame. Who has 10.1.1.1?"
- Demo commands: `ip addr`, `arp -n`

**Section 3: Ansible 101 with Jinja2 (3 min):**
- Why automate? "We have 2 routers. What if we had 200?"
- Show inventory.yml: "This tells Ansible WHAT to configure"
- Show host_vars/srl1.yml: "This tells Ansible the DATA for each device"
- Show templates/srl_interfaces.json.j2: "This is the TEMPLATE -- one template, many devices"
- Walk through the Jinja2 loop: `{% for iface in interfaces %}` + `{{ iface.ipv4_address }}`
- Key insight: "The template is the same for every router. Only the variables change. That's the power of templating."

**Section 4: Live Demo -- Deploy and Configure (3 min):**
```bash
cd lessons/clab/02-ip-fundamentals
containerlab deploy -t topology/lab.clab.yml
cd ansible
ansible-playbook -i inventory.yml playbook.yml
```
- Show the Ansible output (per-router config applied)
- Verify on srl1: `docker exec -it clab-ip-fundamentals-srl1 sr_cli -c "show interface brief"`
- Show interfaces are up with IPs

**Section 5: Verification (2 min):**
```bash
# Adjacent ping -- works!
docker exec clab-ip-fundamentals-host1 ping -c 3 10.1.1.1

# Cross-subnet ping -- fails!
docker exec clab-ip-fundamentals-host1 ping -c 3 10.1.3.2
```
- Explain: "host1 sends to its gateway (srl1), but srl1 doesn't know how to reach 10.1.3.0/24. It only knows about its directly connected subnets. That's what routing solves."
- Show ARP table: `docker exec clab-ip-fundamentals-host1 arp -n`

**Recap (30s):**
> "Today we covered layers 1-4 of the networking stack, configured IP addresses using Ansible with Jinja2 templates, and discovered that devices can only talk directly on the same subnet. For everything else, you need routing -- and that's exactly what we'll build in lesson 3."

**Closing (30s):**
> exercises folder, break/fix challenges, commit to your fork

**Post-Recording Checklist, B-Roll notes, Editing notes**

**Step 2: Commit**

```bash
git add lessons/clab/02-ip-fundamentals/script.md
git commit -m "feat(lesson-02): add video script"
```

---

### Task 7: Final commit and PR

**Step 1: Verify all files exist**

```bash
find lessons/clab/02-ip-fundamentals -type f | sort
```

Expected files:
```
lessons/clab/02-ip-fundamentals/README.md
lessons/clab/02-ip-fundamentals/ansible/host_vars/srl1.yml
lessons/clab/02-ip-fundamentals/ansible/host_vars/srl2.yml
lessons/clab/02-ip-fundamentals/ansible/inventory.yml
lessons/clab/02-ip-fundamentals/ansible/playbook.yml
lessons/clab/02-ip-fundamentals/ansible/templates/srl_interfaces.json.j2
lessons/clab/02-ip-fundamentals/exercises/README.md
lessons/clab/02-ip-fundamentals/solutions/README.md
lessons/clab/02-ip-fundamentals/tests/test_ip_fundamentals.py
lessons/clab/02-ip-fundamentals/script.md
```

**Step 2: Create feature branch and push**

```bash
git checkout -b feature/lesson-02-ip-fundamentals
git push -u origin feature/lesson-02-ip-fundamentals
```

**Step 3: Create PR**

```bash
gh pr create --base main --title "feat: add lesson 02 - IP Fundamentals & Basic Connectivity" --body "$(cat <<'EOF'
## Summary
- New lesson covering OSI layers 1-4, IP addressing, and Ansible with Jinja2 templates
- 4-node topology: host1--srl1--srl2--host2 across three subnets
- Ansible playbook uses Jinja2 templates to generate SR Linux CLI commands via JSON-RPC
- 6 exercises including 3 break/fix troubleshooting scenarios
- pytest validation tests for environment, topology, Ansible structure, and connectivity

## Lesson(s) Affected
- Added: lessons/clab/02-ip-fundamentals/

## Test plan
- [ ] Topology files tested with containerlab
- [ ] Ansible playbook applies config successfully
- [ ] Adjacent pings verified working
- [ ] Cross-subnet ping verified failing (expected -- no routing yet)
- [ ] Break/fix exercises verified
- [ ] Automated tests pass
- [ ] Video script reviewed for accuracy
EOF
)"
```
