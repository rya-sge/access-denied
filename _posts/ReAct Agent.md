---
layout: post
title: ReAct Agent, Reason and Act
date:   2025-01-14
lang: en
locale: en-GB
categories: programmation
tags: ReAct LLMs agent
description: ReAct is a general paradigm to combine reasoning(Reason)and acting (Act) with language models for solving diverse language reasoning and decision making tasks.
image: /assets/article/mlg/react-agent-schema.png
isMath: false
---

ReAct is a general paradigm to combine reasoning (**Reason**) and acting (**Act**) with language models for solving diverse language reasoning and decision making tasks. It was introduced in the paper [REAC T: SYNERGIZING REASONING AND ACTING IN LANGUAGE MODELS](https://arxiv.org/abs/2210.03629) / [pdf](https://arxiv.org/pdf/2210.03629)

ReAct prompts LLMs to generate both verbal reasoning traces and actions pertaining to a task in an interleaved manner, which allows the model to perform dynamic reasoning to create, maintain, and adjust high-level plans for acting (reason to act), while also interact with the external environments (e.g. Wikipedia) to incorporate additional information into reasoning (act to reason).

Another type of framework to solve tasks are:

| Method                                                       | Description                                                  | Limitation                                                   |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Standard                                                     | Directly the answer by the mode, no access to the external environment | Can give wrong answers due to hallucination,                 |
| Chain-of-thought (CoT, Reason Only)<br />[arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903) | The “chain-of-thought” reasoning is a static black box, in that the model uses its own internal representations to generate thoughts and is not grounded in the external world | Limits its ability to reason reactively or update its knowledge. <br />This can lead to issues like fact hallucination and error propagation over the reasoning process |
| Act-only                                                     | Access to the external environment but don't reason on the answers get | Can fails despite the access of real-world web interaction, due to a lack of reasoning to guide how to interact with the Internet for QA. |



## Common Features

Since decision making and reasoning capabilities are integrated into a large language model, ReAct enjoys several unique features: 

### Intuitive and easy to design

Designing ReAct prompts is straightforward as human annotators just type down their thoughts in language on top of their actions taken. 

### General and flexible

Due to the flexible thought space and thought-action occurrence format, ReAct works for diverse tasks with distinct action spaces and reasoning needs, including but not limited to QA, fact verification, text game, and web navigation. 

### Performant and robust

ReAct shows strong generalization to new task instances while learning solely from one to six in-context examples, consistently outperforming baselines with only reasoning or acting across different domains. 

### Human aligned and controllable

ReAct promises an interpretable sequential decision making and reasoning process where humans can easily inspect reasoning and factual correctness. Moreover, humans can also control or correct the agent behavior on the go by thought editing.

### Basic schema

Here a basic schema to show the difference between a Reason Only framework, an Act Only framework and finally the ReAct framework which uses reasoning and actions to find the best solution.

Schema from [colab - Introduction to ReAct Agents with Gemini & Function Calling](https://colab.research.google.com/github/GoogleCloudPlatform/generative-ai/blob/main/gemini/function-calling/intro_diy_react_agent.ipynb)

![react-agent-schema]({{site.url_complet}}/assets/article/mlg/react-agent-schema.png)

### Example with Gemini

This paragraph is mainly taken from this article [Building ReAct Agents from Scratch: A Hands-On Guide using Gemini](https://medium.com/google-cloud/building-react-agents-from-scratch-a-hands-on-guide-using-gemini-ffe4621d90ae) with the following github [GitHub]( https://github.com/arunpshankar/react-from-scratch)

![react-agent-gemini]({{site.url_complet}}/assets/article/mlg/react-agent-gemini.png)

The ReAct Agent framework can be divided in several steps:

1. **Input**: The agent starts by receiving a task by the user in natural language. This task goes into the core language model (LLM), like Gemini Pro, which interprets what needs to be done. 
2. **Reasoning**: The LLM analyzes the task and breaks it down into steps. It plans which actions to take and decides how to approach the problem based on available information and tools.
3. **Action with External Environments**: The agent will use the main environment available (e.g google Search and Wikipeida in this project). With these tools, the agent can find relevant information or get additional context.
4. **Observation and Memory**: After executing each action, the agent observes the results and saves relevant information in its memory. Therefore, it can use this context to improve its answer and its future actions. 
5. **Feedback Loop**: The agent cycles through reasoning, action, and observation steps continuously. Every time it gathers new information, it goes back to the reasoning stage, where the LLM considers the updated knowledge. This iterative loop helps the agent refine its approach and stay aligned with the task. The reasoning loop can be either constrained based on an end condition or capped by max iterations. 
6. **Response**: Finally, once it has gathered enough information and reached a solid understanding, the agent generates a response based on all the information it has collected and refined over multiple cycles. The final decision will depend:
   - Solely decided by the LLM 
   - Based on an end condition, 
   - or we may fail to arrive at an outcome given the constrained number of iterations.

![react-think_act_observe_loop]({{site.url_complet}}/assets/article/mlg/react-think_act_observe_loop.png)

## References

- [REAC T: SYNERGIZING REASONING AND ACTING IN LANGUAGE MODELS](https://arxiv.org/abs/2210.03629) / [pdf](https://arxiv.org/pdf/2210.03629)
- [Promp Engineering Guide - ReAct Prompting](https://www.promptingguide.ai/techniques/react)
- [Klu - ReACT Agent Model](https://klu.ai/glossary/react-agent-model)
- [Building ReAct Agents from Scratch: A Hands-On Guide using Gemini](https://medium.com/google-cloud/building-react-agents-from-scratch-a-hands-on-guide-using-gemini-ffe4621d90ae)
- [Hugging face - How do multi-step agents work?](https://huggingface.co/docs/smolagents/en/conceptual_guides/react)