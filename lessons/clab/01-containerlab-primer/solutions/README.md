# Lesson 1 Solutions

Reference solutions for the Containerlab Primer exercises.

## Exercise 2: Three-Node Topology

**File: `three-node.clab.yml`**

```yaml
name: three-node-lab

topology:
  nodes:
    srl1:
      kind: srl
      image: ghcr.io/nokia/srlinux:24.10.1

    srl2:
      kind: srl
      image: ghcr.io/nokia/srlinux:24.10.1

    srl3:
      kind: srl
      image: ghcr.io/nokia/srlinux:24.10.1

  links:
    # srl1 to srl2
    - endpoints: ["srl1:e1-1", "srl2:e1-1"]
    # srl2 to srl3
    - endpoints: ["srl2:e1-2", "srl3:e1-1"]
```

**Verification:**
```bash
docker exec -it clab-three-node-lab-srl2 sr_cli -c "show interface brief"
```

Expected output shows both `ethernet-1/1` and `ethernet-1/2`.

---

## Exercise 4: Resources

**SR Linux Documentation:**
https://containerlab.dev/manual/kinds/srl/

Key configuration options:
- `startup-config`: Path to configuration file
- `license`: Path to license file (not needed for basic features)
- `type`: SR Linux variant (ixrd1, ixrd2, etc.)

**Example Community Labs:**
- https://github.com/srl-labs/srl-labs - Nokia's official examples
- https://github.com/srl-labs/containerlab/tree/main/lab-examples - Built-in examples
- https://clabs.netdevops.me/ - Community lab collection

---

## Exercise 5: Mixed Topology

**File: `mixed-topology.clab.yml`**

```yaml
name: mixed-lab

topology:
  nodes:
    router:
      kind: srl
      image: ghcr.io/nokia/srlinux:24.10.1

    host1:
      kind: linux
      image: alpine:latest

  links:
    - endpoints: ["router:e1-1", "host1:eth1"]
```

**Verification steps:**

1. Deploy:
   ```bash
   containerlab deploy -t exercises/mixed-topology.clab.yml
   ```

2. Check router:
   ```bash
   docker exec -it clab-mixed-lab-router sr_cli -c "show interface brief"
   ```

3. Check host:
   ```bash
   docker exec -it clab-mixed-lab-host1 ip addr show eth1
   ```

Expected host output:
```
3: eth1@if7: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 9500 qdisc noqueue state UP
    link/ether aa:c1:ab:xx:xx:xx brd ff:ff:ff:ff:ff:ff link-netnsid 0
```

Note: The interface exists but has no IP address assigned. That's normal - we'll configure IP addresses in Lesson 2.

---

## Key Takeaways

1. **Topology files are YAML** - Easy to read, version control, and template
2. **Lab names matter** - They're used in container names: `clab-<name>-<node>`
3. **Interface naming:**
   - SR Linux: `e1-1` = `ethernet-1/1`
   - Linux: `eth1`, `eth2`, etc.
4. **Mixed topologies work** - Combine network OS and standard Linux containers
5. **Inspect is your friend** - Always verify what's running with `containerlab inspect`
