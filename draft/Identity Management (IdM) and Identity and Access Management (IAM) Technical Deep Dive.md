# Identity Management (IdM) and Identity and Access Management (IAM): Technical Deep Dive

Reference: https://tryhackme.com/room/iaaaidm

Identity Management (IdM) includes all the necessary policies and technologies for identification, authentication, and authorisation. IdM aims to ensure that authorised people have access to the assets and resources needed for their work while unauthorised people are denied access. IdM requires that each user or device is assigned a digital identity.

IdM helps organisations protect sensitive data and maintain compliance with regulations. It also allows organisations to streamline user access processes, reduce costs associated with identity management, and improve user experience. By implementing an effective IdM strategy, organisations can ensure that their users are authenticated and authorised to securely access the resources they need.

Some sources refer to IdM and Identity and Access Management (IAM) interchangeably. Other sources consider IdM to be more focused on the security issues related to user identity, such as authentication and permissions. They state that IdM is concerned with managing the attributes and permissions of users, devices, and groups, while IAM is more concerned with evaluating the attributes and permissions and granting or denying access according to the company policy. In this task, we present them as different, although the line between them tends to be vague.

## Identity Management (IdM)



## Identity and Access Management (IAM)

IAM is a more comprehensive concept than IdM. It encompasses all the processes and technologies to manage and secure digital identities and access rights. IAM systems include a variety of functions, such as user provisioning, access control, identity governance, and compliance management. IAM systems ensure that only authorised users have access to specific resources and data and that their access is monitored and controlled.

IAM systems provide a comprehensive solution to manage and secure access to resources in an organisation. They integrate with multiple systems and applications, providing a centralised view of user identities and access rights. IAM systems use various technologies to manage access, including role-based access control, multi-factor authentication, and single sign-on.

IAM systems help organisations comply with regulatory requirements such as HIPAA, GDPR, and PCI DSS. They provide functionalities to manage the lifecycle of user identities, including onboarding, offboarding, and access revocation. In addition, IAM systems allow organisations to track and audit user activity, which helps to prevent security breaches and ensure compliance with industry regulations.

IdM and IAM are essential components of cybersecurity. They ensure that only authorised individuals have access to specific resources and information. IdM systems manage user identities, while IAM systems encompass broader functions to manage and secure digital identities and access rights.

## Summary

| Topic                 | Details                                                      |
| --------------------- | ------------------------------------------------------------ |
| **IdM Purpose**       | Manage digital identities, handle user provisioning, authentication, and authorisation |
| **IAM Purpose**       | Provide complete access lifecycle control, compliance enforcement, and governance |
| **Technologies Used** | Directories (LDAP/AD), MFA, SSO, RBAC, Identity Governance, Identity Repositories |
| **Key Benefits**      | Regulatory compliance, reduced access risk, streamlined user lifecycle management |
| **Scope Comparison**  | IdM: Identity-centric; IAM: Policy and access governance across multiple systems |



------

## Identity Management (IdM)

**Identity Management (IdM)** is a discipline focused on the creation, maintenance, and deletion of digital identities for users, devices, and services. It ensures that every entity within an IT environment has a verifiable and manageable identity.

IdM is an essential component of cybersecurity that refers to the process of managing and controlling digital identities. It involves the management of user identities, their authentication, authorisation, and access control. 

- The main goal of IdM is to ensure that only authorised individuals have access to specific resources and information. 
- IdM systems are used to manage user identities across an organisation’s network.
- IdM systems use a centralised database to store user identities and access rights. 
- They also provide functionalities to manage and monitor user access to resources. 
- IdM systems generally include features such as user provisioning, authentication, and authorisation.
  -  User provisioning refers to the process of creating and managing user accounts, while authentication and authorisation refer to verifying the identity of a user and granting access to specific resources.

IdM systems are critical in organisations where there are multiple systems and applications that require access control. They help to simplify the management of user identities, reducing the risk of unauthorised access to resources. In addition, IdM systems provide a single point of reference for user identity management, which makes it easier for organisations to manage user access rights.

###  Core Functions of IdM

| Function                      | Description                                                  |
| ----------------------------- | ------------------------------------------------------------ |
| **User Provisioning**         | Automates account creation and role assignment based on user roles or events (e.g., onboarding, transfers) |
| **Authentication**            | Verifies the identity of a user or device using methods like passwords, certificates, biometrics, or tokens |
| **Authorisation**             | Assigns permissions and access levels based on roles, policies, or group memberships |
| **Identity Repository**       | Stores identity records and attributes in a structured form, often using LDAP or Active Directory |
| **Directory Services**        | Maintain searchable, hierarchical identity data, commonly used for access policies |
| **Self-service Capabilities** | Enables users to update profiles, reset passwords, and request access with minimal administrator intervention |



###  Use Cases

- Managing contractor and employee identities across multiple systems
- Ensuring consistent identity attributes across HR, IT, and security systems
- Automating identity deactivation when employees leave the organisation

------

## Identity and Access Management (IAM)

> **Identity and Access Management (IAM)** expands on IdM by integrating identity functions with access controls, governance, auditing, and compliance mechanisms. IAM platforms are designed to control who can access what, under what conditions, and for how long.

IAM is a more comprehensive concept than IdM. It encompasses all the processes and technologies to manage and secure digital identities and access rights. IAM systems include a variety of functions, such as user provisioning, access control, identity governance, and compliance management. 

- IAM systems ensure that only authorised users have access to specific resources and data and that their access is monitored and controlled.
- IAM systems provide a comprehensive solution to manage and secure access to resources in an organisation. They integrate with multiple systems and applications, providing a centralised view of user identities and access rights. 
- IAM systems use various technologies to manage access, including role-based access control, multi-factor authentication, and single sign-on.
- IAM systems help organisations comply with regulatory requirements such as HIPAA, GDPR, and PCI DSS. 
- They provide functionalities to manage the lifecycle of user identities, including onboarding, offboarding, and access revocation. In addition, IAM systems allow organisations to track and audit user activity, which helps to prevent security breaches and ensure compliance with industry regulations.

IdM and IAM are essential components of cybersecurity. They ensure that only authorised individuals have access to specific resources and information. IdM systems manage user identities, while IAM systems encompass broader functions to manage and secure digital identities and access rights.

### Key Components of IAM

| Component                             | Description                                                  |
| ------------------------------------- | ------------------------------------------------------------ |
| **Access Control**                    | Implements fine-grained rules (e.g., RBAC, ABAC) to control access to data, apps, or systems |
| **Single Sign-On (SSO)**              | Allows users to log in once and access multiple services without repeated authentication |
| **Multi-Factor Authentication (MFA)** | Requires two or more identity verification factors (e.g., password + OTP) |
| **Identity Governance**               | Provides tools to review access rights, certify entitlements, and enforce SoD (Segregation of Duties) |
| **Lifecycle Management**              | Covers onboarding, role changes, and offboarding, ensuring timely updates to access rights |
| **Audit and Compliance**              | Tracks and logs identity activities, supports reporting for standards like GDPR, HIPAA, PCI DSS |



### Access Control Models in IAM

- **Role-Based Access Control (RBAC):** Grants access based on predefined roles (e.g., HR manager)
- **Attribute-Based Access Control (ABAC):** Considers attributes like location, time, or device type
- **Policy-Based Access Control:** Applies dynamic policies combining multiple conditions

------

## IdM vs IAM: A Clearer Separation

Some sources treat IdM and IAM as synonyms, but this distinction is increasingly important in complex IT environments:

| Feature                 | IdM                                             | IAM                                                          |
| ----------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| **Scope**               | Identity creation and management                | Full lifecycle of identity and access control                |
| **Focus**               | "Who" the user is and what attributes they have | "Who can access what and under what conditions"              |
| **Core Components**     | Provisioning, identity stores, authentication   | Provisioning, authentication, SSO, MFA, governance, auditing |
| **System Integration**  | Typically works with fewer systems              | Integrates with enterprise systems (ERP, cloud apps, VPN, etc.) |
| **Compliance Coverage** | Limited                                         | Strong—supports audits, policy enforcement, access certifications |



------

## PlantUML Mind Map

```
plantumlCopyEdit@startmindmap
* Identity Management & IAM
** Identity Management (IdM)
*** Digital Identity
**** Users
**** Devices
**** Services
*** Core Functions
**** User Provisioning
**** Authentication
**** Authorisation
**** Identity Repository
**** Directory Services
*** Tools
**** LDAP
**** Active Directory
**** SCIM Protocol
** Identity and Access Management (IAM)
*** Access Control
**** Role-Based (RBAC)
**** Attribute-Based (ABAC)
**** Policy-Based
*** Authentication Enhancements
**** Multi-Factor Authentication (MFA)
**** Single Sign-On (SSO)
*** Identity Governance
**** Access Reviews
**** Segregation of Duties
**** Attestation
*** Lifecycle Management
**** Onboarding
**** Role Changes
**** Offboarding
*** Compliance
**** GDPR
**** HIPAA
**** PCI DSS
*** Audit and Monitoring
**** Logging
**** Reporting
** Benefits
*** Reduced Risk
*** Compliance Assurance
*** Access Automation
*** Cost Reduction
@endmindmap
```

------

## 🧩 Strategic Importance

Implementing IdM and IAM systems is essential for:

- Preventing unauthorised access to sensitive systems and data
- Enforcing least privilege principles
- Automating identity-related workflows
- Maintaining continuous compliance with regulatory frameworks

IAM platforms often integrate with cloud providers, business applications, and endpoint systems, providing a unified framework for identity lifecycle and access enforcement.

------

## 🏁 Conclusion

**Identity Management** handles the establishment and control of digital identities, focusing on provisioning, authentication, and basic access rights. **Identity and Access Management** builds upon this by incorporating advanced controls, identity governance, compliance support, and monitoring.

Together, they form the foundation of modern access control and security architecture. As organisations