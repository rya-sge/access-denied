---
layout: post
title: Mutual TLS (mTLS) - Overview
date:   2024-12-16
lang: en
locale: en-GB
categories: security cryptography
tags: tls mtls cloud
description: Mutual TLS (mTLS) is an extension of the standard TLS protocol which requires both the client and server to present and validate certificates, enabling mutual authentication.  
image: 
isMath: false
---

Transport Layer Security (TLS) is widely used to ensure encrypted and secure communication between clients and servers. While traditional TLS focuses primarily on securing the server, **Mutual TLS (mTLS)** adds an additional layer by authenticating both the server and the client. mTLS is often used in a [Zero Trust](https://www.cloudflare.com/learning/security/glossary/what-is-zero-trust/) security framework 

This approach enhances security but introduces specific challenges. 

This article explores mTLS, its advantages, and how it compares to classical TLS.

If you want to know more about TLS, particulary the version 1.3, you can also read my article [TLS 1.3 - Overview](https://rya-sge.github.io/access-denied/2024/11/04/TLS1.3-overview/) and [rfc8446](https://datatracker.ietf.org/doc/html/rfc8446)

> Warning: this article is still in draft state and its content is still mainly taken from several different sources and ChatGPT with a few edits of my own. Its content should become more personal later.

------

#### What is mTLS?

Mutual TLS (mTLS) is an extension of the standard TLS protocol. 

In classical TLS, a client verifies the identity of a server using the server’s digital certificate, but the server does not verify the client. 

mTLS modifies this process by requiring both the client and server to present and validate certificates, enabling mutual authentication. 

This ensures that both parties in the communication are trusted.

------

#### How mTLS Works

1. **Handshake Process**:
   - Both parties exchange their certificates during the TLS handshake.
   - Each party verifies the other’s certificate using a trusted Certificate Authority (CA).
   - Once verified, a secure, encrypted communication channel is established.
2. **Authentication**:
   - The client uses its private key to sign a challenge provided by the server, proving its identity.
   - The server validates the signed challenge using the client’s certificate.
3. **Encryption**:
   - After authentication, a symmetric encryption key is generated and used to encrypt the communication.

------

#### Advantages of mTLS

1. **Enhanced Security**:
   - By requiring mutual authentication, mTLS protects against unauthorized access from both ends.
   - It is particularly effective in preventing **man-in-the-middle attacks** and ensuring the authenticity of both parties.
2. **Ideal for Zero Trust Architectures**:

In a zero-trust model, no entity is trusted by default. mTLS fits perfectly by requiring verification of every entity communicating within the network.

3. **Resistance to Credential Theft**:

Since authentication relies on certificates rather than usernames and passwords, it mitigates risks associated with stolen or weak credentials.

4. **Improved Trust in APIs**:

In microservices and API ecosystems, mTLS ensures secure service-to-service communication by verifying every microservice.

------

#### Disadvantages of mTLS

1. **Complexity of Implementation**:
   - Deploying mTLS requires managing certificates for both clients and servers, significantly increasing operational complexity.
   - Mismanagement of certificates can lead to outages or security gaps.
2. **Scalability Challenges**:
   - As the number of clients grows, maintaining an up-to-date certificate authority and revoking compromised certificates can become difficult.
   - Rotating certificates across large systems demands careful coordination.
3. **Higher Costs**:
   - The need for an infrastructure to manage certificates, such as a Public Key Infrastructure (PKI), adds to operational expenses.
   - Training staff and adapting legacy systems to support mTLS may incur additional costs.
4. **Compatibility Issues**:
   - Not all clients or systems natively support mTLS, which might require additional software or configuration adjustments.
5. **Latency Overhead**:
   - The mTLS handshake is more computationally intensive than traditional TLS, potentially increasing latency, especially in high-frequency communications.

------

#### Comparison: mTLS vs. Classical TLS

| Feature            | Classical TLS                                                | mTLS                                                         |
| ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Authentication** | Server-only authentication                                   | Mutual (client and server)                                   |
| **Security**       | Secure communication for data transit                        | Enhanced security through mutual verification, protecting against man-in-the-middle attacks |
| **Role of CA**     | CAs issue and sign only server certificates                  | CAs issue and sign both server and client certificates       |
| **Complexity**     | Easier since only the server must be authenticate, a self-signed root can be used | More complex since the client must  be authenticated too     |
| **Scalability**    | Scales well with many clients                                | Requires additional effort for certificate management        |
| **Use Cases**      | Web browsing, general client-server communication            | API security, microservices, zero-trust environments         |

Reference: [SSL2Buy - What is mTLS? How Does It Differ From TLS?](https://www.ssl2buy.com/wiki/what-is-mtls-how-does-it-differ-from-tls)

#### **Use Cases for mTLS**

1. **Microservices and APIs**:

Ensures secure communication in distributed systems where multiple services interact.

2. **Critical Systems**:

Used in environments requiring stringent access control, such as banking or healthcare systems.

3. **IoT Devices**:

Prevents unauthorized devices from connecting to critical infrastructure.

4. **Zero Trust Networks**:

Enforces authentication for every connection within the network, adhering to zero-trust principles.

## Kubernates with MTLS

In Kubernetes, **mTLS** (mutual TLS) can be added across services by using a **service mesh** like **Istio**,**[Linkerd](https://linkerd.io/2-edge/features/automatic-mtls/)**, **[Hashicorp - Consul Connect](https://developer.hashicorp.com/consul/docs/connect/ca)**, or **[Kuma](https://kuma.io/docs/2.10.x/policies/mutual-tls/)**.
 Here’s the big picture:

- Kubernetes **by itself** doesn’t enforce mTLS between Pods/Services.
- A **service mesh** injects **sidecar proxies** (e.g., Envoy) next to your apps and **automatically encrypts** all service-to-service communication with **mutual TLS**.
- This way, all internal traffic is authenticated and encrypted **without** the applications themselves having to deal with certificates directly.

For example, with **Istio**:

- You install Istio on your cluster.
- It injects an **Envoy proxy** next to each Pod (transparent sidecar).
- The proxies negotiate certificates issued by Istio’s built-in **CA** (Certificate Authority).
- Then, all traffic between services happens **over mTLS**, even if the apps know nothing about TLS.

And bonus: you can define **fine-grained policies** — like saying "only service A can call service B".

See also: [Secure Application Communications with Mutual TLS and Istio](https://istio.io/latest/blog/2023/secure-apps-with-istio/)

------

#### Conclusion

mTLS offers significant advantages in terms of security and trust, making it a powerful tool in environments where authentication and data integrity are paramount. However, its complexity, cost, and scalability challenges mean it’s not always the right choice for every application. Organizations must carefully evaluate their security needs, infrastructure, and resources when deciding between mTLS and classical TLS architectures. For highly sensitive or distributed systems, the benefits of mTLS often outweigh its challenges, ensuring robust, end-to-end protection.

## References

- [What is mTLS? How Does It Differ From TLS?](https://www.ssl2buy.com/wiki/what-is-mtls-how-does-it-differ-from-tls)
- [Cloudflare - What is mutual TLS (mTLS)?](https://www.cloudflare.com/learning/access-management/what-is-mutual-tls/)
- [Secure Application Communications with Mutual TLS and Istio](https://istio.io/latest/blog/2023/secure-apps-with-istio/)
- ChatGPT with the input "Write me an article about mTLS, its advantage and disadvatange compare to a classical TLS architecture", "how can add mtls to kubernates through a service mesh"