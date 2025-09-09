Of course. Here is the text formatted in Markdown.

# RESP protocol description

RESP (REdis Serialization Protocol) is essentially a serialization protocol that supports several data types. In RESP, the first byte of data determines its type.

Redis generally uses RESP as a request-response protocol in the following way:

* Clients send commands to a Redis server as an array of bulk strings.
* The first (and sometimes also the second) bulk string in the array is the command's name.
* Subsequent elements of the array are the arguments for the command.
* The server replies with a RESP type.
* The reply's type is determined by the command's implementation and possibly by the client's protocol version.

---

## Protocol Details

RESP is a binary protocol that uses control sequences encoded in standard ASCII. The `A` character, for example, is encoded with the binary byte of value 65. Similarly, the characters CR (`\r`), LF (`\n`) and SP (` `) have binary byte values of 13, 10 and 32, respectively. The `\r\n` (CRLF) is the protocol's terminator, which always separates its parts.

The first byte in an RESP-serialized payload always identifies its type. Subsequent bytes constitute the type's contents.

---

## Data Types

We categorize every RESP data type as either **simple**, **bulk** or **aggregate**.

* **Simple types** are similar to scalars in programming languages that represent plain literal values. Booleans and Integers are such examples.
* **RESP strings** are either simple or bulk.
    * **Simple strings** never contain carriage return (`\r`) or line feed (`\n`) characters.
    * **Bulk strings** can contain any binary data and may also be referred to as binary or blob. Note that bulk strings may be further encoded and decoded, e.g. with a wide multi-byte encoding, by the client.
* **Aggregates**, such as Arrays and Maps, can have varying numbers of sub-elements and nesting levels.

The following table summarizes the RESP data types that Redis supports:

| RESP data type   | Minimal protocol version | Category  | First byte |
| ---------------- | ------------------------ | --------- | :--------: |
| Simple strings   | RESP2                    | Simple    |    `+`     |
| Simple Errors    | RESP2                    | Simple    |    `-`     |
| Integers         | RESP2                    | Simple    |    `:`     |
| Bulk strings     | RESP2                    | Aggregate |    `$`     |
| Arrays           | RESP2                    | Aggregate |    `*`     |
| Nulls            | RESP3                    | Simple    |    `_`     |
| Booleans         | RESP3                    | Simple    |    `#`     |
| Doubles          | RESP3                    | Simple    |    `,`     |
| Big numbers      | RESP3                    | Simple    |    `(`     |
| Bulk errors      | RESP3                    | Aggregate |    `!`     |
| Verbatim strings | RESP3                    | Aggregate |    `=`     |
| Maps             | RESP3                    | Aggregate |    `%`     |
| Attributes       | RESP3                    | Aggregate |    `\|`     |
| Sets             | RESP3                    | Aggregate |    `~`     |
| Pushes           | RESP3                    | Aggregate |    `>`     |
