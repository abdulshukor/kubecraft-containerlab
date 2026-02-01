# Lesson 0 Solutions

Reference solutions for the Docker Networking exercises.

## Exercise 1: Default Bridge Answers

**Why does ping by name fail?**
The default bridge network does NOT provide automatic DNS resolution. Only custom bridge networks have the embedded DNS server that resolves container names.

**Default bridge IP range:**
Typically `172.17.0.0/16`. The gateway is usually `172.17.0.1`.

---

## Exercise 2: Custom Bridge Answers

**Gateway IP:** Typically `172.18.0.1` (or next available 172.x.0.1)

**Subnet:** Usually a /16 like `172.18.0.0/16`

**Difference from default bridge:**
- Automatic DNS resolution (can ping by name)
- Better isolation (only containers explicitly added can communicate)
- User-defined, so you control the configuration

---

## Exercise 3: Multi-Network Answers

**Why can appserver reach both?**
Appserver is connected to BOTH the frontend and backend networks. It has interfaces on each network, so it can route to containers on either.

**Number of interfaces:**
Three:
1. `lo` - loopback (always present)
2. `eth0` - frontend network
3. `eth1` - backend network (added by `docker network connect`)

Verify:
```bash
docker exec appserver ip addr
```

**Topology diagram:**

```
┌─────────────────────────────────────────┐
│           frontend network              │
│  ┌───────────┐      ┌───────────┐       │
│  │ webserver │      │ appserver │       │
│  └───────────┘      └─────┬─────┘       │
└───────────────────────────┼─────────────┘
                            │
┌───────────────────────────┼─────────────┐
│           backend network │             │
│                     ┌─────┴─────┐       │
│                     │ appserver │       │
│                     └───────────┘       │
│  ┌───────────┐                          │
│  │ database  │                          │
│  └───────────┘                          │
└─────────────────────────────────────────┘
```

---

## Exercise 4: Docker Compose Answers

**Compose network naming convention:**
`<project>_<network-name>`

If your directory is `00-docker-networking`, networks will be:
- `00-docker-networking_public`
- `00-docker-networking_internal`

**Exposing web on port 8080:**

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"
    networks:
      - public
```

---

## Exercise 5: Challenge Solution

**Problem identification:**
`broken-web` is on the default bridge network, while `broken-client` is on `app-network`. They're on different networks and cannot communicate.

**Fix:**
```bash
docker network connect app-network broken-web
```

**Verification:**
```bash
docker exec broken-client wget -qO- http://broken-web
```

**Alternative fix (also valid):**
```bash
docker network connect bridge broken-client
```

Then use the IP address since default bridge doesn't have DNS.

---

## Key Takeaways

1. **Default bridge has no DNS** - Use custom networks for name resolution
2. **Networks provide isolation** - Containers on different networks can't talk (without explicit connection)
3. **Containers can join multiple networks** - Useful for services that bridge concerns
4. **Docker Compose manages networks** - Declarative approach, automatic DNS within the compose project
5. **`docker network connect`** - Add containers to networks without restarting
