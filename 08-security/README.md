# Security
A key component of ColonyOS is a crypto identity protocol, inspired by Bitcoin and Ethereum. The signature signing, verification, and recovery crypto protocol is compatible with Ethereum, allowing for future integration with a blockchain.

Each user, colony, and executor is assigned a digital identity verified by the Colonies server using [implicit certificates](https://en.wikipedia.org/wiki/Implicit_certificate) implicit certificates based on [Elliptic-curve cryptography](https://en.wikipedia.org/wiki/Elliptic-curve_cryptography). This setup enables the reconstruction of public keys from signatures, and identities are then calculated as cryptographic hashes (SHA3-256) of these reconstructed public keys. The Colonies server doesn't store private keys but keeps the identities in a database, verifying that identities reconstructed from RPC calls match those stored. This ensures secure and authenticated interactions within the ColonyOS environment.

This protocol works as follows. Let's assume a user has the following id, and the Colonies server has stored the id in its internal database.

```console
69383f17554afbf81594999eec96adbaa0fc6caace5f07990248b14167c41e8f
```

To add a colony, the user (or Colonies SDK) calculates a signature of the message using the user's private key and sends the RPC message to the Colonies server.

```json
{
    "payloadtype": "addcolonymsg",
    "payload": "ewogICAgICBjb2xvbnlpZDogYWM4ZGM4OTQ5YWYzOTVmZDUxZWFkMzFkNTk4YjI1MmJkYTAyZjFmNmVlZDExYWNlN2ZjN2RjOGRkODVhYzMyZSwKICAgICAgbmFtZTogdGVzdF9jb2xvbnlfbmFtZQogIH0=",
    "signature": "82f2ba6368d5c7d0e9bfa6a01a8fa4d4263113f9eedf235e3a4c7b1febcdc2914fe1f8727746b2f501ceec5736457f218fe3b1a469dd6071775c472a802aa81501"
}
```

Upon receiving the RPC message, the Colonies server reconstructs the identity from the received data. It then cross-verify the reconstructed identity against its database to verify if the caller possesses the necessary rights to add a new colony. This process ensures that only authorized users can access the system.

## Access control
In ColonyOS, there are four defined roles, each with specific responsibilities and levels of access:

* **Colonies server owner:** Analogous to super root user, this role involves owning and maintaining a Colonies server(s).
* **Colony owner:** Comparable to root users, they are individuals or entities owning individual colonies. One server can host multiple colonies.
* **Colony user members:** Members of a specific colony, potentially ranging from one to several in each colony.
* **Colony executor members:** Executors within a specific colony, with each colony possibly having multiple executors.

In ColonyOS, each role is associated with a private key, and specific rules determine how these roles can interact with the Colonies server:

### Server owner rules:
- Only the server owner can register a new colony.
- Only the server owner can list all registered colonies.

### Colony owner rules:
- Only a colony owner can register a user or executor to their colony.
- Only a colony owner can approve or disapprove an executor within their colony.

### User rules:
- Any user member of a colony can submit, get, and list processes or workflows within their colony.

### Executor rules:
- Any executor member of a colony can submit, get, assign, and list processes or workflows within their colony.
- Only an executor can be assigned a process.
- Only the executor that was assigned a process can set attributes on that process or mark it as complete/failed.

## Generating private keys
```bash
colonies key generate
```

```console
INFO[0000] Generated new private key                     Id=ca31a36c4b1aec586c5e420678405e37407c3770d89d19ecd7d7fce5e16ad80f PrvKey=b6bc335d32f78f3184e002a9d1c2e411c4eb55e0cc69e0cc630e355ab6922561
```

It is also possible to derive the id given a private key.

```bash
 colonies key id --prvkey b6bc335d32f78f3184e002a9d1c2e411c4eb55e0cc69e0cc630e355ab6922561
```

```console
INFO[0000] Corresponding Id for the given private key    Id=ca31a36c4b1aec586c5e420678405e37407c3770d89d19ecd7d7fce5e16ad80f
```

## Changing keys
It possible to change keys using the **chid** subcommand, e.g:

```bash
colonies user chid --userid ca31a36c4b1aec586c5e420678405e37407c3770d89d19ecd7d7fce5e16ad80f  
```

```bash
colonies executor chid --executorid ca31a36c4b1aec586c5e420678405e37407c3770d89d19ecd7d7fce5e16ad80f  
```

```bash
colonies colony chid --colonyid ca31a36c4b1aec586c5e420678405e37407c3770d89d19ecd7d7fce5e16ad80f  
```

```bash
colonies server chid --serverid ca31a36c4b1aec586c5e420678405e37407c3770d89d19ecd7d7fce5e16ad80f  
```

Note that the *docker-compose.env* must be modified after running this command. 
