# IMB HSM

IBM Cloud® Hyper Protect Crypto Services is a dedicated key management service and Hardware Security Module (HSM) that provides you with the Keep Your Own Key capability for cloud data encryption. 

Built on FIPS 140-2 Level 4 certified hardware, Hyper Protect Crypto Services provides you with exclusive control of your encryption keys.

## Main concepts

### **1. Hardware Security Modules (HSMs)**

Dedicated hardware devices that perform cryptographic operations in a physically secure environment. In Hyper Protect Crypto Services, they’re **single-tenant and customer-controlled**, meaning only you—not IBM—can access the encryption keys.

------

### **2. FIPS 140-2 Level 4 Certification**

The highest U.S. government security rating for cryptographic modules, ensuring tamper resistance and automatic key erasure if physical breach is attempted. 

This certifies that IBM’s HSMs meet the strictest security standards available in the industry.

------

### **3. PKCS #11 API**

An industry-standard API for cryptographic operations such as signing, encryption, and key management. 

Because Hyper Protect Crypto Services supports it directly, applications already using PKCS #11 can integrate without code changes.

------

### **4. GREP11 (Enterprise PKCS #11 over gRPC)**

A modern, remote-access version of PKCS #11 using gRPC for high-performance communication. 

It provides scalable access to HSM functions while preserving compatibility with existing PKCS #11-based applications.

------

### **5. Key Management and Keep Your Own Key (KYOK)**

Includes key creation, import, rotation, and deletion—plus the ability to fully own your master keys with no IBM access. 

This guarantees data sovereignty: when you delete keys, data becomes permanently unrecoverable.

------

### **6. Secure Service Container (SSC)**

A LinuxONE technology that isolates workloads at the hardware level to block even system administrators from viewing sensitive data. 

It ensures privileged-user lockout, protecting against insider threats.

------

### **7. Bring Your Own Key (BYOK)**

Lets you import your existing encryption keys into IBM Cloud. 

This allows you to maintain complete control of cryptographic material while using IBM cloud services.

------

### **8. Access Control and Auditing**

Integrates with IBM Cloud IAM for fine-grained permissions and with IBM Cloud Activity Tracker for monitoring. 

These features ensure compliance, enforce least-privilege access, and provide full visibility into key usage.

------

### **9. Cryptographic Operations in Hardware**

Functions like key generation, encryption/decryption, digital signing, and signature verification are executed inside tamper-resistant HSMs. 

This provides hardware-level assurance that sensitive keys never leave secure boundaries.

------

### **10. Security Certifications (EAL4+)**

The HSM also meets Common Criteria Evaluation Assurance Level 4+, an international standard proving resistance to real-world attacks. 

This strengthens regulatory compliance and customer trust.