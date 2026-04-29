# VPN

The internet plays a *gargantuan* role in modern life, with most people being connected in some way virtually constantly. As such, most public spaces (e.g. cafés, restaurants, public transport) are fully equipped with public WiFI to let people catch up on email (or, equally likely, play the latest hit mobile game). What many people *don't* realise is that expecting public WiFi to be available can prove to be very dangerous indeed.

Public WiFi, whilst incredibly handy, also gives an attacker ideal opportunities to attack other users' devices or simply intercept and record traffic to steal sensitive information. This latter technique can be as simple as exploiting the fact that most people *expect* to see public networks available. The attacker can quickly set up a network of their own and monitor the traffic of everyone who connects; this is referred to as a "man-in-the-middle" attack and is very easy to carry out. For example, if you were to connect to a network belonging to an attacker then logged into an account for a website that doesn't use an encrypted (HTTPS) connection, the attacker could simply pluck your credentials out of the network traffic and use them to log into your account for themselves. This scenario will be explored in more detail in the interactive element to this task; however, it is fortunately significantly less likely to occur with modern websites which implement **T**ransport **L**ayer **S**ecurity (TLS) to encrypt traffic between their servers and users as standard.

Equally, being connected to any network (regardless of whether you trust it or not) makes your device visible to others on the network. You never know who else is on a public network or what their intentions might be

The *ideal* solution to this problem is simply not connecting to untrusted networks. Beneficial though public wireless connections are, it will always be safer to use a mobile hotspot or private network. Unfortunately, the ideal solution is not always feasible; when this is the case, we must rely on other methods of staying safe.

**V**irtual **P**rivate **N**etworks (VPNs) encrypt all traffic leaving and re-entering your machine, rendering any interception techniques useless as the intercepted data will simply look like gibberish. Whilst it is possible to host your own VPN server for free, most people prefer to use one of the many online solutions. Some of these commercial solutions are free, but be warned: free VPNs tend not to provide the best security and often harvest your data themselves to make a profit. That said, the price of a good VPN is more than worth it for the increased safety when operating on untrusted networks. There are many good options around, including [ProtonVPN](https://protonvpn.com/) and [Mullvad VPN](https://mullvad.net/en/), to name two.



Your VPN encrypted all of the traffic entering and leaving your computer, stopping the attacker from being able to read any sensitive information, even if intercepted;

https://tryhackme.com/r/room/commonattacks