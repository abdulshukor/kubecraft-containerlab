# Lesson 0 Exercises: Docker Networking

Complete these exercises to reinforce your Docker networking knowledge.

## Exercise 1: Explore Default Networking

**Objective:** Understand the default bridge network behavior.

### Steps

1. Run two containers on the default network:
   ```bash
   docker run -d --name container1 alpine sleep 3600
   docker run -d --name container2 alpine sleep 3600
   ```

2. Get their IP addresses:
   ```bash
   docker inspect container1 --format='{{.NetworkSettings.IPAddress}}'
   docker inspect container2 --format='{{.NetworkSettings.IPAddress}}'
   ```

3. Try to ping by IP (should work):
   ```bash
   docker exec container1 ping -c 2 <container2-ip>
   ```

4. Try to ping by name (should fail):
   ```bash
   docker exec container1 ping -c 2 container2
   ```

### Questions

- Why does ping by name fail on the default bridge?
- What IP range does the default bridge use?

### Cleanup
```bash
docker rm -f container1 container2
```

---

## Exercise 2: Custom Bridge Network

**Objective:** Create a custom network with DNS resolution.

### Steps

1. Create a custom network:
   ```bash
   docker network create lab-network
   ```

2. Run containers on your custom network:
   ```bash
   docker run -d --name web --network lab-network nginx
   docker run -d --name client --network lab-network alpine sleep 3600
   ```

3. Test DNS resolution:
   ```bash
   docker exec client ping -c 2 web
   ```

4. Test HTTP connectivity:
   ```bash
   docker exec client wget -qO- http://web
   ```

5. Inspect the network:
   ```bash
   docker network inspect lab-network
   ```

### Questions

- What gateway IP does your custom network use?
- What subnet was assigned?
- How is this different from the default bridge?

### Cleanup
```bash
docker rm -f web client
docker network rm lab-network
```

---

## Exercise 3: Multi-Network Container

**Objective:** Connect a container to multiple networks.

### Steps

1. Create two networks:
   ```bash
   docker network create frontend
   docker network create backend
   ```

2. Create containers:
   ```bash
   docker run -d --name webserver --network frontend nginx
   docker run -d --name database --network backend alpine sleep 3600
   docker run -d --name appserver --network frontend alpine sleep 3600
   ```

3. Connect appserver to backend as well:
   ```bash
   docker network connect backend appserver
   ```

4. Test connectivity from appserver:
   ```bash
   # Should work (both on frontend)
   docker exec appserver ping -c 2 webserver

   # Should work (both on backend)
   docker exec appserver ping -c 2 database
   ```

5. Test connectivity from webserver to database:
   ```bash
   # Should fail (different networks)
   docker exec webserver ping -c 2 database
   ```

### Questions

- Why can appserver reach both webserver and database?
- How many network interfaces does appserver have?
- Check with: `docker exec appserver ip addr`

### Diagram Your Setup

Create a simple diagram showing the network topology.

### Cleanup
```bash
docker rm -f webserver appserver database
docker network rm frontend backend
```

---

## Exercise 4: Docker Compose Networking

**Objective:** Define networks declaratively with Docker Compose.

### Steps

1. Create a file `docker-compose.yml`:
   ```yaml
   version: "3.8"

   services:
     web:
       image: nginx
       networks:
         - public

     api:
       image: alpine
       command: sleep 3600
       networks:
         - public
         - internal

     db:
       image: alpine
       command: sleep 3600
       networks:
         - internal

   networks:
     public:
     internal:
   ```

2. Start the stack:
   ```bash
   docker compose up -d
   ```

3. Test connectivity:
   ```bash
   # api can reach web
   docker compose exec api ping -c 2 web

   # api can reach db
   docker compose exec api ping -c 2 db

   # web cannot reach db
   docker compose exec web ping -c 2 db
   ```

4. List the networks created:
   ```bash
   docker network ls | grep -E "public|internal"
   ```

### Questions

- What naming convention does Compose use for networks?
- How would you expose the web service on port 8080?

### Cleanup
```bash
docker compose down
```

---

## Exercise 5: Challenge - Network Debugging

**Objective:** Practice debugging network connectivity issues.

### Scenario

A colleague set up containers but they can't communicate. Debug and fix the issue.

### Setup (Run This Exactly)

```bash
docker network create app-network
docker run -d --name broken-web nginx
docker run -d --name broken-client --network app-network alpine sleep 3600
```

### Your Task

1. Identify why `broken-client` cannot reach `broken-web`
2. Fix the issue without recreating the containers
3. Verify connectivity works

### Hints

- Check which network each container is on
- Remember: `docker network connect`

### Solution Check

```bash
docker exec broken-client wget -qO- http://broken-web
```

If you see HTML output, you've fixed it!

### Cleanup
```bash
docker rm -f broken-web broken-client
docker network rm app-network
```

---

## Validation

Run the automated tests to verify your understanding:

```bash
cd /workspaces/kubecraft/lessons/clab/00-docker-networking
pytest tests/
```

## Completion Checklist

- [ ] Exercise 1: Explored default bridge
- [ ] Exercise 2: Created custom network with DNS
- [ ] Exercise 3: Connected container to multiple networks
- [ ] Exercise 4: Used Docker Compose for networking
- [ ] Exercise 5: Debugged network connectivity issue

## Next Steps

Once complete, proceed to [Lesson 1: Containerlab Primer](../01-containerlab-primer/).
