# cachica: A Redis-Inspired In-Memory Key-Value Store

## 🚀 Project Overview

cachica is an ambitious personal project to build a high-performance, in-memory key-value data store from scratch, heavily inspired by the architecture and protocol of Redis. Developed in Python using `asyncio`, it aims to provide a robust learning platform for understanding non-blocking I/O, network protocol design, and concurrent state management.

This project serves as a foundational step towards building more complex distributed systems, demonstrating proficiency in low-level system design and performance optimization.

## ✨ Features (Planned)

* **Asynchronous TCP Server**: Built with `asyncio` for efficient handling of many concurrent client connections.
* **RESP-like Protocol**: Implements a subset of the Redis Serialization Protocol (RESP) for clear, structured communication.
* **Core Key-Value Operations**: Support for `SET`, `GET`, `DEL`, `PING`, `ECHO`.
* **Key Expiration (TTL)**: Ability to set time-to-live for keys (`EX` and `PX` options).
* **Additional Data Structures**: Initial focus on Lists (`LPUSH`, `RPUSH`, `LPOP`, `LRANGE`).
* **Optional C Extension**: Exploration of integrating a C-based hash table for critical performance paths.

## 🎯 Project Roadmap & Implementation Milestones

This project will be developed in distinct phases, with clear objectives for each.

### Phase 1: The Network Foundation (Core Server & Basic Protocol) ✅

**Goal**: Establish a stable `asyncio` TCP server capable of receiving and parsing basic commands using a RESP-like protocol.

* [x] Initialize `asyncio` event loop and start a TCP server.
* [x] Implement a basic `ConnectionHandler` to manage individual client connections.
* [x] Develop a `ProtocolParser` to read incoming bytes from the client stream.
* [x] Implement parsing for RESP Simple Strings and Bulk Strings.
* [x] Successfully parse a `PING` command and send back a `PONG`.
* [x] Successfully parse `ECHO "message"` and send back the message.
* [x] Basic logging for server events and client interactions.

### Phase 2: The Core Engine (In-Memory Store & Basic Commands) ◀️

**Goal**: Implement the central in-memory data store and handlers for fundamental key-value operations.

* [x] Create a `DataStore` class (using a Python `dict` initially) to hold all key-value pairs.
* [x] Implement a `Command Dispatcher` to dispatch parsed commands to the correct `DataStore` methods.
* [x] Implement `SET key value` functionality, storing the key-value pair in the `DataStore`.
* [x] Implement `GET key` functionality, retrieving a value or returning `None` if the key doesn't exist.
* [x] Implement `DEL key` functionality, removing a key-value pair.
* [ ] Ensure `DataStore` operations are thread-safe if multi-threading is introduced later (or explicitly mention `asyncio`'s single-threaded nature in this context).
* [ ] Write unit tests for `DataStore` operations.

### Phase 3: Advanced Features (Key Expiration & Lists)

**Goal**: Introduce advanced data management features like time-to-live for keys and a new data structure (Lists).

* [ ] Modify `SET` command to accept `EX seconds` and `PX milliseconds` arguments.
* [ ] Implement an expiration mechanism:
    * Store expiration timestamps alongside values.
    * Develop a background task (e.g., an `asyncio` task) to periodically scan for and evict expired keys.
* [ ] Implement List data type support:
    * Modify `DataStore` to handle lists (e.g., using `collections.deque`).
    * Implement `LPUSH key value [value ...]`.
    * [ ] Implement `RPUSH key value [value ...]`.
    * [ ] Implement `LPOP key`.
    * [ ] Implement `LRANGE key start stop`.
* [ ] Update `ProtocolParser` to handle multi-bulk array commands (e.g., for `LPUSH` with multiple values).
* [ ] Comprehensive unit and integration tests for all new features.

### Phase 4: Optional C Extension (Performance Optimization)

**Goal**: Explore integrating a C-based hash table for critical performance paths as a practice for low-level optimization.

* [ ] Identify a performance-critical component (e.g., the core hash map for `DataStore`).
* [ ] Implement a basic hash table in C.
* [ ] Use Python's C API or `ctypes` to create a Python module wrapper for the C hash table.
* [ ] Integrate the C extension into `DataStore` to replace the Python `dict` for primary key storage.
* [ ] **Benchmark**: Conduct performance tests comparing the Python `dict` implementation vs. the C extension. Document findings.

### Phase 5: Polish & Professionalism

**Goal**: Finalize the project with professional tooling, documentation, and a robust testing suite.

* [ ] Create a simple Python client library to interact with CachePy.
* [ ] Containerize CachePy using Docker.
* [ ] Set up GitHub Actions for Continuous Integration (CI) to run tests automatically.
* [ ] Enhance logging with structured logging (e.g., `logging.config.dictConfig`).
* [ ] Improve `README.md` with architectural diagrams and detailed usage instructions.
* [ ] Add comprehensive docstrings to all functions and classes.
* [ ] Final code review and refactoring for clarity, efficiency, and adherence to PEP 8.

---

