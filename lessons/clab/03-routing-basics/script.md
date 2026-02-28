# Lesson 3: Routing Basics & Static Routes - Video Script

## Lesson Information

| Field | Value |
|-------|-------|
| **Lesson Number** | 03 |
| **Title** | Routing Basics & Static Routes |
| **Duration Target** | 12-15 minutes |
| **Prerequisites** | Lessons 0-2, Ansible installed |
| **Learning Objectives** | Explain routing tables, configure static routes, extend Ansible with routes template, trace multi-hop paths, diagnose routing failures |

---

## Pre-Recording Checklist

- [ ] Lab environment tested (containerlab installed, Docker running)
- [ ] Ansible installed: `ansible --version`
- [ ] SR Linux image pulled: `docker pull ghcr.io/nokia/srlinux:24.10.1`
- [ ] Alpine image pulled: `docker pull alpine:3.20`
- [ ] Lesson 02 lab destroyed (no IP conflicts)
- [ ] Screen resolution set (1920x1080)
- [ ] Terminal font size increased (14-16pt)
- [ ] Notifications disabled
- [ ] Clean terminal: `clear && history -c`
- [ ] No labs running: `containerlab destroy --all`

---

## Script

### Opening Hook (30 seconds)

> **[VOICEOVER - Terminal visible]**
>
> "Last time, we configured IP addresses on our routers and hosts. Everything worked perfectly -- until we tried to ping across subnets. The ping failed. The routers knew about their directly connected networks, but nothing else. Today, we fix that. By the end of this lesson, packets will flow across every subnet in our lab -- and you'll understand exactly how they get there."

**Visual:** Terminal showing the failed cross-subnet ping from lesson 02

---

### Section 1: Routing Table Fundamentals (3 minutes)

> **[VOICEOVER]**
>
> "Every router has a routing table -- think of it as a map. When a packet arrives, the router checks the destination IP against this table and decides where to send it next.
>
> There are two types of entries in a routing table. First, directly connected routes -- these are created automatically when you configure an IP address on an interface. If srl1 has 10.1.1.1/24 on ethernet-1/1, it automatically knows how to reach the 10.1.1.0/24 subnet.
>
> Second, static routes -- these are entries you add manually. They tell the router: 'To reach network X, send the packet to next-hop Y.'
>
> When a router receives a packet, it uses longest prefix match to decide which route to use. If the routing table has both 10.0.0.0/8 and 10.1.5.0/24, and the destination is 10.1.5.2, the router picks 10.1.5.0/24 because it's more specific -- it has the longest matching prefix.
>
> In lesson 2, hosts had default gateways. That's just a static route that says 'for anything I don't know about, send it here.' Routers need the same thing -- entries for every network they need to reach."

**Visual:** Whiteboard/Excalidraw showing routing table with two types of entries

**Key Points:**
- Directly connected = automatic, from interface config
- Static = manual, you add them
- Longest prefix match = most specific route wins
- Default gateway = catch-all route

**Transition:** "Let's see how to configure static routes on SR Linux."

---

### Section 2: Static Routes on SR Linux (2 minutes)

> **[VOICEOVER]**
>
> "SR Linux has a two-step process for static routes. First, you create a next-hop-group -- this is a named object that points to the next-hop IP address. Then you create the static route and attach it to that group.
>
> Here's what it looks like."

```bash
docker exec -it clab-routing-basics-srl1 sr_cli
```
```
enter candidate

# Step 1: Create a next-hop-group
set / network-instance default next-hop-groups group nhg-10-1-4-0-24 admin-state enable
set / network-instance default next-hop-groups group nhg-10-1-4-0-24 nexthop 1 ip-address 10.1.2.2

# Step 2: Create the static route pointing to the group
set / network-instance default static-routes route 10.1.4.0/24 admin-state enable
set / network-instance default static-routes route 10.1.4.0/24 next-hop-group nhg-10-1-4-0-24

commit now
```

> "This tells srl1: to reach the 10.1.4.0/24 subnet, send packets to 10.1.2.2 -- that's srl2. The next-hop-group might seem like extra overhead, but it allows advanced features like ECMP -- multiple next-hops for load balancing -- which we'll see in later lessons.
>
> When to use static routes? Small networks, stub networks, default routes. Once you have more than a handful of routes to manage, you'll want a dynamic routing protocol -- that's BGP, coming in lesson 4."

**Transition:** "But we're not going to type all these routes by hand. Let's automate them."

---

### Section 3: Extending Ansible with Routes (2 minutes)

> **[VOICEOVER]**
>
> "In lesson 2, we used one Jinja2 template for interfaces. Now we're adding a second template for routes. Same pattern, new capability.
>
> First, the data. Each router's host_vars now has a static_routes section alongside interfaces."

```yaml
# ansible/host_vars/srl1.yml
static_routes:
  - prefix: 10.1.4.0/24
    next_hop: 10.1.2.2
    description: host2 subnet via srl2
  - prefix: 10.1.5.0/24
    next_hop: 10.1.3.2
    description: host3 subnet via srl3
```

> "The template auto-generates the next-hop-group names from the prefix. Dots become dashes, slashes become dashes -- so 10.1.4.0/24 becomes nhg-10-1-4-0-24. This keeps the naming consistent and human-readable."

```jinja2
{% for route in static_routes %}
{% set nhg_name = "nhg-" + route.prefix | replace(".", "-") | replace("/", "-") %}
set / network-instance default next-hop-groups group {{ nhg_name }} ...
set / network-instance default static-routes route {{ route.prefix }} ...
{% endfor %}
```

> "The playbook gets a second task that renders this template and pushes it via JSON-RPC, just like the interfaces task. We add a guard -- 'when static_routes is defined' -- so routers without routes don't fail."

**Key Points:**
- Same Ansible pattern: data in host_vars, logic in template
- Template auto-generates next-hop-group names
- Second playbook task, same API call pattern
- `when: static_routes is defined` guard

**Transition:** "Let's see it all come together."

---

### Section 4: Live Demo -- Deploy and Configure (3 minutes)

> **[VOICEOVER]**
>
> "We have a hub-and-spoke topology. srl1 is the hub with three interfaces. srl2 and srl3 are spokes, each with a host behind them. Five subnets total."

```bash
cd lessons/clab/03-routing-basics
containerlab deploy -t topology/lab.clab.yml
```

> "Six containers are starting -- three SR Linux routers and three Alpine hosts."

**Expected output:** Table showing 6 running containers

```bash
cd ansible
ansible-playbook -i inventory.yml playbook.yml
```

> "Ansible configures interfaces first, then static routes, then verifies the routing table. Watch the output -- you'll see 'Interface configuration applied' and 'Static routes applied' for each router."

**Expected output:** Ansible play recap showing successful tasks

> "Now let's test. Remember, in lesson 2, cross-subnet ping failed. Let's try it now."

```bash
docker exec clab-routing-basics-host1 ping -c 3 10.1.4.2
docker exec clab-routing-basics-host1 ping -c 3 10.1.5.2
docker exec clab-routing-basics-host2 ping -c 3 10.1.5.2
```

> "All three work. host1 can reach host2 across the hub. host1 can reach host3. And host2 can reach host3 through the hub -- the spoke-to-spoke path. That's the lesson 2 cliffhanger resolved."

---

### Section 5: Multi-Hop Packet Trace (2 minutes)

> **[VOICEOVER]**
>
> "Let's trace exactly how a packet gets from host2 to host3. This is the longest path -- spoke to spoke through the hub.
>
> Step 1: host2 wants to reach 10.1.5.2. That's not on its local subnet, so it sends the packet to its default gateway -- 10.1.4.1, which is srl2.
>
> Step 2: srl2 receives the packet and looks up 10.1.5.0/24 in its routing table. It finds a static route: next-hop 10.1.2.1. That's srl1 -- the hub. srl2 forwards the packet.
>
> Step 3: srl1 receives the packet and looks up 10.1.5.0/24. Static route: next-hop 10.1.3.2. That's srl3. Forward again.
>
> Step 4: srl3 receives the packet and looks up 10.1.5.0/24. This time it's a directly connected subnet -- ethernet-1/2. srl3 delivers the packet directly to host3.
>
> But that's only half the story. host3 needs to send a reply back. The return path follows the same chain in reverse: host3 to srl3 to srl1 to srl2 to host2. Every router makes its own independent forwarding decision. And if any router in the chain is missing a route -- the reply gets dropped and the ping fails. Both directions must work."

**Visual:** Diagram showing packet flow with numbered hops

---

### Recap (30 seconds)

> **[VOICEOVER]**
>
> "Let's recap:
>
> - Routing tables contain directly connected and static routes. Longest prefix match selects the best route.
> - Static routes need both a next-hop-group and a route entry on SR Linux.
> - Ansible templates automate route configuration just like interface configuration.
> - Every hop makes an independent decision, and both the forward and return path must work."

---

### Closing (30 seconds)

> **[VOICEOVER]**
>
> "Head to the exercises folder. You'll verify end-to-end connectivity, read routing tables, and then tackle four break/fix scenarios -- missing routes, wrong next-hops, routing loops, and unreachable links. Each one teaches a different way routing can go wrong.
>
> In the next lesson, we'll see why static routes don't scale. When you have hundreds of routers, you need routes to update automatically -- and that's where dynamic routing protocols come in.
>
> Happy labbing!"

**Visual:** Show exercises folder

---

## Post-Recording Checklist

- [ ] Lab destroyed: `containerlab destroy --all`
- [ ] Timing verified: ~12-15 minutes
- [ ] All commands worked correctly
- [ ] Transcript updated with actual output

---

## B-Roll / Supplementary Footage Needed

1. Hub-and-spoke topology diagram (Excalidraw) with numbered subnets
2. Routing table visualization -- show packet arriving, table lookup, forwarding decision
3. Packet trace animation -- show packet hopping through 4 routers with TTL decrement
4. Split screen: routing table before static routes (only local) vs after (local + static)
5. Routing loop animation -- packet bouncing between two routers until TTL expires

---

## Notes for Editing

- **0:00-0:30** - Hook, overlay failed ping from lesson 02
- **0:30-3:30** - Routing tables, use Excalidraw for routing table diagram
- **3:30-5:30** - SR Linux CLI, show actual terminal
- **5:30-7:30** - Ansible extension, split screen for template + host_vars
- **7:30-10:30** - Live demo, full terminal
- **10:30-12:30** - Packet trace, overlay diagram with numbered steps
- **End** - Call-to-action overlay for exercises
