---
layout: post
title: AI security and threats
date:   2025-01-22
lang: en
locale: en-GB
categories: security ai
tags: security threat ai
description:  AI brings with it a range of new challenges and security concerns. From the creation of realistic deepfakes to vulnerabilities like prompt injection and the emergence of unregulated "Shadow AI" systems.
image: /assets/article/blockchain/ai/chatbot/chatbot-car.png
isMath: false
---

Artificial Intelligence (AI) has become an integral part of modern life, driving advancements across industries and reshaping how we interact with technology. 

However, as AI continues to evolve, it brings with it a range of new challenges and security concerns. From the creation of realistic deepfakes to vulnerabilities like prompt injection and the use of "Shadow AI" systems inside an organisation, these issues highlight the need for vigilance and proactive measures. 

This article examines the potential risks posed by AI technologies and considers strategies to address them effectively.

This article has been made from 4 video by IBM

- [How Chatbots Could Be 'Hacked' by Corpus Poisoning](https://www.youtube.com/watch?v=RTCaGwxD2uU)
- [What is Shadow AI? The Dark Horse of Cybersecurity Threats](https://www.youtube.com/watch?v=YBE6hq-OTFI)
- [Unmask The DeepFake: Defending Against Generative AI Deception](https://www.youtube.com/watch?v=cVvJgdm19Ak)
- [What Is a Prompt Injection Attack?](https://www.youtube.com/watch?v=jrHRe9lSqqA)

Then: 

- A transcript has been generated with [NoteGPT](https://notegpt.io/)
- A more formal article has been made with ChatGPT from this transcript
- Finally, I have perform a few addition and personal notes.

[TOC]

## How Chatbots Could Be 'Hacked' by Corpus Poisoning

> **Corpus poisoning** is a method of corrupting or manipulating the data used to train or fine-tune machine learning models, particularly those that rely on large language models (LLMs) or generative AI systems. By introducing malicious, biased, or deceptive content into the training dataset—known as the **corpus**—attackers can influence the behavior and outputs of the AI system.

Not everything you read on the Internet is true. While this isn’t a shocking revelation, it underscores the challenge of distinguishing reliable sources from misleading or outright false information. 

Traditionally, when searching for answers, people turn to search engines like Google. These platforms present a mix of reliable sources, questionable links, and advertisements, leaving users to sift through results to find credible information.

Enter AI-driven chatbots, such as ChatGPT, which offer a streamlined alternative: concise, authoritative-sounding answers without the noise of ads or the need for manual filtering. While this simplicity is appealing, it introduces a critical vulnerability—the risk of corpus poisoning.

Chatbots rely on vast knowledge bases, or corpora, to generate responses. These corpora aggregate information from diverse sources, making them foundational to the chatbot’s accuracy. However, if bad actors subtly corrupt the corpus with misinformation, the chatbot’s output can be compromised. Unlike glaring errors that users might easily detect, these subtle manipulations blend in, eroding trust incrementally.

### Example

#### Mixing household cleaning products

For instance, consider asking a chatbot about mixing household cleaning products. Under normal circumstances, the bot might suggest a safe formula using common ingredients like baking soda and vinegar. But in a corpus poisoning scenario, altered data could lead the chatbot to recommend mixing ammonia and bleach—a toxic combination with potentially severe health consequences. While this example might seem hypothetical, it illustrates the potential risks when users overly rely on AI systems without verifying their outputs.

#### Programming

**Corpus poisoning** extends beyond household tips. 

In programming, for example, a chatbot could be exploited to provide code snippets containing hidden vulnerabilities or malware. Developers trusting these outputs without scrutiny could unwittingly introduce security flaws into their software.

### Conclusion

This growing reliance on chatbots necessitates a renewed emphasis on trust but verify. Users must demand greater observability, transparency, and accountability from AI systems, including mechanisms for citation and source verification. 

In an ideal world, chatbots would not only provide answers but also “show their work,” enabling users to trace the origin of their recommendations and make informed decisions.

While AI chatbots hold immense promise for simplifying information retrieval, they are not immune to exploitation. As we embrace these tools, vigilance and critical thinking remain our best defenses against the insidious risks of corpus poisoning.



-----

## What is Shadow AI? The Dark Horse of Cybersecurity Threats

> Shadow AI refers to the unsanctioned or unmonitored use of artificial intelligence tools within an organization. These are AI systems or models that employees or teams deploy without the approval, knowledge, or oversight of the organization's IT or security departments. While Shadow AI can stem from well-intentioned efforts to innovate or streamline workflows, it introduces significant risks to cybersecurity, compliance, and operational integrity.

It’s 2 o’clock in the morning, and here’s a question: do you know where your AI is? Many organizations assume they have full control over the AI tools within their environments, but the reality is often more complex. Enter Shadow AI—the unsanctioned or untracked use of AI systems within a corporate environment.

Generative AI's potential has inspired employees to explore ways to leverage it for various tasks. However, not all of these initiatives are approved or monitored by IT and security teams. These shadow projects, while innovative, pose significant cybersecurity risks, including the potential for data leaks or exposure to vulnerabilities. Organizations must discover and assess all instances of AI in their environments—especially the ones flying under the radar—to secure and manage them effectively.

### First step - Discovery

To tackle this challenge, the first step is discovery. Businesses should start by mapping out the cloud environments they operate, as these are common locations for hosting powerful, compute-intensive AI models. Shadow AI deployments often involve a model, data used for training and tuning, and applications leveraging the model. Identifying these components is crucial.

Furthermore, open-source models downloaded from platforms like Hugging Face may not follow the same security protocols as full-fledged AI platforms such as IBM’s watsonx. These differences necessitate tailored approaches for securing various AI implementations. By using automated tools for discovery and visualization, companies can illuminate the dark corners where Shadow AI operates.

### Second step - Secure against risk

Once Shadow AI systems are identified, organizations must secure them against risks like data exfiltration, access mismanagement, and even adversarial attacks such as data poisoning. 

Ensuring robust access controls and enforcing the principle of least privilege can minimize these risks. 

Additionally, businesses should consider providing sanctioned alternatives to unsanctioned AI tools, as saying "no" often drives employees to seek unapproved solutions.

Ultimately, visibility and control are key. Organizations must implement security posture management for AI systems, ensuring that these tools benefit the business without introducing avoidable risks. 

By shining a light on Shadow AI, companies can turn potential threats into assets, fostering innovation while maintaining robust security practices.

-----

## What Is a Prompt Injection Attack?

> Prompt injection occurs when an attacker inserts malicious instructions into the input to alter the AI’s behavior. 

Prompt injection attacks exploit the flexibility of AI systems, particularly those powered by large language models (LLMs). 

These systems generate responses based on input prompts, but their design can make them susceptible to malicious manipulation. 

### Example

A striking example involved a chatbot at a car dealership. A user cleverly tricked the chatbot by instructing it to agree with everything the customer said and declare every statement as a legally binding agreement. Following this setup, the user proposed buying an SUV for $1, and the chatbot dutifully responded, “Yes, we have a deal, and that's a legally binding agreement.” 

![chatbot-car]({{site.url_complet}}/assets/article/blockchain/ai/chatbot/chatbot-car.png)

See [Chris Bakke on X](https://x.com/ChrisJBakke/status/1736533308849443121)

While this may seem absurd, it highlights a serious vulnerability—AI systems can be “socially engineered” into behaving contrary to their intended programming.

### Description

Prompt injection occurs when an attacker inserts malicious instructions into the input to alter the AI’s behavior. 

These attacks often exploit the blurred boundaries between training data and user instructions inherent in LLMs. For example, attackers might prompt the AI to perform unauthorized actions, bypassing safeguards designed to prevent harmful behavior. 

More sophisticated forms of this attack include “jailbreaking,” where users coerce the AI into operating outside its ethical and security constraints, such as generating malware or misinformation.

The implications of prompt injection attacks are profound. They can lead to data leakage, the dissemination of false or dangerous information, and even remote system hijacking. 

### Conclusion

Addressing this threat requires a multi-faceted approach: curating high-quality training data, implementing robust input validation, and integrating human oversight. As AI evolves, combating prompt injection will remain an ongoing challenge, akin to an arms race between developers and attackers.

See [The Washington Post - The clever trick that turns ChatGPT into its evil twin](https://www.washingtonpost.com/technology/2023/02/14/chatgpt-dan-jailbreak/)

----

## Unmask the DeepFake: Defending Against Generative AI Deception

> A **deepfake** is a synthetic media created using artificial intelligence (AI) to manipulate or replicate a person’s likeness, voice, or mannerisms in a highly realistic way. The term "deepfake" is derived from the combination of "deep learning," a type of AI that enables the technology, and "fake," indicating the fabricated nature of the content.

"Hi, this is Jeff, and you are listening to a deepfake of my voice." 

If that sentence made you pause, then it’s done its job. It’s an example of how generative AI can convincingly mimic someone’s voice, turning a few seconds of audio into a tool for deception. Deepfakes—AI-generated audio, video, or images that convincingly replicate real people—are no longer science fiction. They are a growing threat, accessible to anyone with basic technology skills and a phone.

#### How DeepFakes Work

Creating a deepfake starts with training an AI model using samples of a person’s voice or video. For audio, this might involve recording someone speaking a set of phrases. The AI analyzes the sample, learning patterns in tone, pitch, and rhythm to mimic the voice. Advanced models need as little as three seconds of audio to create a believable replica. Once trained, the AI can generate new audio or video by inputting any text the creator wants the deepfake to say.

Deepfakes are not limited to audio. Video deepfakes go a step further, simulating facial expressions, lip movements, and mannerisms. As the technology improves, these creations become harder to distinguish from genuine recordings.

#### Risks Posed by DeepFakes

Deepfakes are not merely an amusing novelty; they carry serious risks:

1. **Financial Fraud**
   Deepfake scams can lead to significant monetary losses. For example, a "grandparent scam" might use a deepfake of a family member’s voice to urgently request money. Similarly, corporations have fallen victim to fake video calls from executives, leading to multimillion-dollar losses.
2. **Disinformation Campaigns**
   Deepfakes can fuel disinformation on a massive scale. Imagine a fabricated video of a head of state declaring war or a CEO admitting to product failures. These manipulations could influence elections, destabilize markets, or incite public panic.
3. **Extortion and Blackmail**
   Cybercriminals can exploit deepfakes to fabricate compromising material, threatening victims with reputational harm unless they pay a ransom.
4. **Judicial Challenges**
   The existence of deepfakes introduces doubt into legal proceedings. Jurors might wrongfully convict or acquit based on fake evidence, or conversely, defense attorneys could claim genuine evidence is fake, eroding trust in the judicial system.

#### Can Technology Solve the Problem?

The natural response to a technological threat is to turn to technology for solutions. However, deepfake detection tools face significant challenges:

- **Accuracy Issues**: Many detection tools struggle to maintain accuracy. A study by NPR revealed that some tools were no better than a coin toss, achieving only 50% accuracy.
- **The Arms Race**: As detection tools improve, so do deepfake generators, making it a perpetual race with no clear winner.
- **Implementation Challenges**: Proposals like digital watermarks or authentication labels sound promising but require global standards, compliance, and widespread adoption—obstacles that are difficult to overcome.

#### Practical Defenses Against DeepFakes

If technology alone can’t solve the problem, what can we do?

1. **Public Education**
   Awareness is the first line of defense. People must understand the capabilities and risks of deepfakes to approach unfamiliar media with healthy skepticism. For example, if you weren’t physically present for an event or conversation, question whether what you saw or heard is authentic.
2. **Out-of-Band Verification**
   When stakes are high, verify information through independent channels. If you receive a suspicious voice call, hang up and call the person back using a trusted number. Similarly, corroborate unusual stories through multiple sources.
3. **Pre-Shared Code Words**
   Families or organizations can agree on a secret phrase or code word to authenticate sensitive communications. While not foolproof, this method adds an extra layer of security.
4. **Healthy Skepticism**
   Adopting a cautious mindset is essential. Treat any unverified audio or video as suspect, particularly when it prompts urgent action like transferring money or sharing sensitive information.

#### Preparing for the Future

Deepfakes represent a significant escalation in the cyber arms race. The technology is improving rapidly, and while detection tools may not always keep pace, vigilance and critical thinking remain vital. By educating the public, verifying information, and fostering skepticism, we can mitigate the risks posed by generative AI deception.

As the saying goes, forewarned is forearmed. Deepfakes may create uncertainty, but awareness and proactive measures can help us navigate this new frontier securely.

## References

IBM Video:

- [How Chatbots Could Be 'Hacked' by Corpus Poisoning](https://www.youtube.com/watch?v=RTCaGwxD2uU)
- [What is Shadow AI? The Dark Horse of Cybersecurity Threats](https://www.youtube.com/watch?v=YBE6hq-OTFI)
- [Unmask The DeepFake: Defending Against Generative AI Deception](https://www.youtube.com/watch?v=cVvJgdm19Ak)
- [What Is a Prompt Injection Attack?](https://www.youtube.com/watch?v=jrHRe9lSqqA)

[NoteGPT](https://notegpt.io/) for the transcript

ChatGTP with the input

- Explain what is shadow ai ?
- What Is a Deepfake?
- Explain Corpus Poisoning 