# Lesson 05 Restructure: RFC 7938 Compliance and Script Accuracy

**Date:** 2026-03-22
**Status:** Approved
**Scope:** Lesson 05 (Spine-Leaf BGP) -- script, README, exercises, solutions, gNMIc configs, topology comment

## Problem

Lesson 05 has multiple technical inaccuracies identified during review:

1. **Claims to follow RFC 7938 but doesn't.** The lab assigns unique ASNs per spine (65100, 65101), but RFC 7938 Section 5.2.1 says all spines share a single ASN. Each leaf gets a unique ASN.
2. **"Why unique ASN" paragraph inverts cause and effect.** Says unique ASNs are for "simplicity" — the actual reason is that eBGP requires different ASNs on each side by definition. RFC 7938 chose eBGP because it re-advertises freely without route reflectors.
3. **Full-mesh strawman in Section 1.** Extrapolates lesson 04's 3-router topology to "50 routers, 1225 links" — nobody would full-mesh a data center. Lesson 04 was hub-and-spoke (full mesh only after exercise 3).
4. **TTL/hop count contradiction.** Says "minus 3 hops" and "exactly 2 router hops" in the same narration.
5. **export-bgp transit role unexplained.** The policy that makes spines function as transit routers is listed without explanation.
6. **Policy chaining never introduced.** The `next-policy` default action on `export-connected` is SR Linux-specific and never explained, but referenced in the recap.
7. **Exercise 4 fix restores wrong export-policy.** Sets `[export-connected]` instead of `[export-connected export-bgp]`.
8. **README video outline uses `docker stop/start`** for spine failure, but script and exercises use `sr_cli` interface disable/enable.
9. **BGP convergence timing unexplained.** Students see fast recovery but don't learn it depends on interface-level detection, not BGP timers.
10. **Jargon without definitions.** Clos, RFC, iBGP, route reflector, router-ID, peer-group, AFI-SAFI used without explanation.

## Design

### ASN Model Change

- Both spines: AS 65000 (shared)
- Leaves: AS 65001-65004 (unique per device, unchanged)
- All spine-leaf links remain eBGP (cross AS boundary)
- Shared spine ASN means identical AS-paths through any spine, simplifying ECMP (no multipath-relax needed)

### Script Structure (Approach B: Split Section 2)

| # | Section | Duration | Changes |
|---|---------|----------|---------|
| Hook | Opening | 30s | No change (already fixed in prior PR) |
| 1 | Why Spine-Leaf? | 2 min | Rewrite: bridge from lesson 04 hub-and-spoke->full-mesh-of-3, pivot to 3-tier/STP as the real predecessor, introduce Clos with Charles Clos attribution |
| 2 | BGP Design Choices (NEW) | 90s | iBGP vs eBGP contrast, route reflector motivation, RFC 7938 recommendation, shared spine ASN + unique leaf ASNs, brief note on RFCs as primary source of truth |
| 3 | Our Fabric (was 2) | 90s | Topology with updated ASNs, remove old "why unique ASN" paragraph, define peer-group and router-ID in passing |
| 4 | Deploying the Fabric (was 3) | 2 min | Renumbered only |
| 5 | Configure and Verify (was 4) | 3 min | Expand policy chain explanation (refresher from lesson 04), explain export-bgp transit role, prefix-set rationale moved here from recap, fix TTL narration, drop AFI-SAFI jargon |
| 6 | Spine Failure (was 5) | 2 min | Add convergence timing note (interface-down vs hold timer, mention BFD) |
| Recap | | 30s | Rewritten to match new framing |
| Closing | | 30s | No change |

**Target duration: 13-15 minutes**

### Section 1: Why Spine-Leaf? (rewrite)

- Open with lesson 04's actual progression: started hub-and-spoke, exercise 3 added the srl2-srl3 link making it a full mesh of 3
- One sentence acknowledging full mesh gives redundancy but doesn't scale (no fake math about 50 routers)
- Pivot to real history: 3-tier core/distribution/access with STP was the actual data center standard
- STP blocks redundant links to prevent loops -- you pay for cables, then half are disabled
- Clos spine-leaf: all links active via ECMP, predictable hop count, tiers scale independently
- Define Clos on first use: "named after Charles Clos, who published this non-blocking switch design in 1953"

### Section 2: BGP Design Choices (new section)

Narrative arc:

1. **Frame the question:** We need a routing protocol for this fabric. Lesson 4 used eBGP. Could we use iBGP instead?
2. **iBGP's catch:** If every device shared one ASN, all sessions would be iBGP. iBGP won't re-advertise a route learned from one iBGP peer to another. Spine1 learns leaf1's subnet but won't pass it to leaf2. Fix: full iBGP mesh (doesn't scale) or route reflector (adds complexity).
3. **RFCs as source of truth:** Brief note that RFCs (Requests for Comments) are how internet protocols are documented and standardized -- the primary source of truth for how things actually work. Encourage students to read them.
4. **RFC 7938's answer:** Published 2016, documents how large-scale data centers (Microsoft, Facebook) solved this: eBGP for everything. Each leaf gets its own ASN. Spines share a single ASN -- they never peer with each other, so no iBGP between them. Every spine-leaf link crosses an AS boundary = eBGP.
5. **Why this is better:** Routes re-advertised freely, no route reflectors needed. Loop prevention via AS-path. Shared spine ASN means identical AS-paths through any spine = equal-cost paths for ECMP.

### Section 3: Our Fabric (updated from old Section 2)

- Both spines labeled AS 65000, leaves 65001-65004
- Remove old "Why a unique AS per device?" paragraph (covered in Section 2)
- Define peer-group and router-ID in passing on first mention
- Session count: 8 (4 leaves x 2 spines), unchanged
- Note: each leaf's peer-as for both spine neighbors is 65000

### Section 5: Configure and Verify (fixes)

- Policy chain explanation as a refresher from lesson 04: export-connected runs first, matching host /24s via the host-subnets prefix-set. Non-matching routes fall through via `next-policy` to export-bgp, which accepts BGP-learned routes.
- Explain export-bgp's critical transit role: "This is what makes spines work as transit routers. Without it, spine1 learns leaf1's subnet but never announces it to other leaves. SR Linux's default-deny export means nothing advertises without explicit policy."
- Prefix-set rationale here (not deferred to recap): /31 fabric links filtered out because they're already known via direct connection.
- TTL fix: "TTL is 61: starting at 64, decremented once by each of the 3 routers in the path -- leaf1, the spine, and leaf4. The leaf-to-leaf path is 2 fabric hops, but hosts see 3 router hops end-to-end."
- Use "IPv4 unicast address family" instead of AFI-SAFI jargon.

### Section 6: Spine Failure (addition)

- After describing packet loss during convergence, add: "Recovery is fast here because disabling an interface triggers an immediate TCP teardown -- the BGP session drops instantly. In production, you'd configure BFD -- Bidirectional Forwarding Detection -- for sub-second failure detection. Without it, BGP's default hold timer is 90 seconds."

### Recap (rewrite)

- Clos architecture: structured 2-tier, predictable latency, all links active. Named after Charles Clos, 1953.
- RFC 7938 eBGP: chosen because it re-advertises freely without route reflectors. Spines share ASN 65000, each leaf gets its own.
- ECMP: shared spine ASN = identical AS-paths. SR Linux requires explicit multipath maximum-paths.
- Policy chaining: export-connected filters host subnets, falls through to export-bgp for transit. SR Linux default-deny.
- Fabric resilience: spine failures degrade capacity not connectivity. Fast recovery depends on interface-level detection, not BGP timers.
- Kubernetes connection: this is the physical underlay beneath pod networking.

## File Changes

### gNMIc configs (`gnmic/configs/`)

| File | Change |
|------|--------|
| `spine1-bgp.json` | `autonomous-system`: 65100 -> 65000, `router-id`: stays 10.0.1.1 |
| `spine2-bgp.json` | `autonomous-system`: 65101 -> 65000, `router-id`: stays 10.0.1.2 |
| `leaf1-bgp.json` | Both spine neighbor `peer-as`: 65100/65101 -> 65000 |
| `leaf2-bgp.json` | Both spine neighbor `peer-as`: 65100/65101 -> 65000 |
| `leaf3-bgp.json` | Both spine neighbor `peer-as`: 65100/65101 -> 65000 |
| `leaf4-bgp.json` | Both spine neighbor `peer-as`: 65100/65101 -> 65000 |

### script.md

- Rewrite Section 1 (full-mesh framing)
- Add Section 2 (BGP Design Choices) -- new content
- Update Section 3 (was 2) with new ASNs, remove old ASN justification paragraph
- Renumber Sections 4-6
- Rewrite Section 5 policy explanation, fix TTL narration
- Add convergence note to Section 6
- Rewrite recap
- Update duration target to 13-15 minutes
- Update editing notes timestamps

### README.md

- BGP design table: both spines ASN 65000
- Mermaid diagram: both spines AS 65000
- Objectives list: change "RFC 7938 ASN-per-device model" to reflect shared spine ASN
- All instances of "ASN-per-device" / "unique ASN per device" updated to describe shared-spine model
- Video outline Section 1: updated framing
- Video outline: add Section 2 (BGP Design Choices)
- Video outline Section 5: `docker stop/start` -> `sr_cli` interface disable/enable
- Section 1 text: same framing fix as script
- Add iBGP vs eBGP context matching script Section 2
- Jargon defined on first use (Clos, RFC, router-ID, peer-group)

### exercises/README.md

- Exercise 1 step 3: update config examination to reference shared spine ASN 65000
- Exercise 4 fix step: `[export-connected]` -> `[export-connected export-bgp]`

### solutions/README.md

- All expected output: spine ASN shows 65000
- BGP neighbor tables: both spine peers show AS 65000
- Exercise 4 fix: restore `[export-connected export-bgp]`
- Key Takeaway #5: update "ASN-per-device" language to describe shared-spine model

### topology/lab.clab.yml

- Comment header: update ASN references to show shared spine AS 65000

### Cleanup

- Delete garbage files in `gnmic/` directory (accidentally created files named with voiceover text)

### Notes

- `maximum-paths` values in gNMIc configs remain unchanged: 4 for spines, 2 for leaves
- "Drop AFI-SAFI jargon" applies to voiceover/narration only; SR Linux CLI commands necessarily use `afi-safi` as the YANG path element
- Duration target of 13-15 minutes accounts for natural rambling/expansion during recording; section estimates sum to ~12.5 minutes of scripted content
