---
layout: post
title: "Cyfrin First Fight 39 - Order Book"
date: 2025-07-11
lang: en
locale: en-GB
categories: solidity blockchain
tags: ctf cyfrin first-fight
description: First Fight 43 - Order Book.
image: 
isMath: false
---

The OrderBook contract is a peer-to-peer trading system designed for ERC20 tokens like wETH, wBTC, and wSOL. Sellers can list tokens at their desired price in USDC, and buyers can fill them directly on-chain.

This article describes the [First Fight 43](https://codehawks.cyfrin.io/c/2025-07-orderbook) from Cyfrin.

The code is available on [GitHub](https://github.com/CodeHawks-Contests/2025-07-orderbook).

[TOC]



## Description

- About the Project

  - **OrderBook.sol:**
  
    The `OrderBook` contract is a peer-to-peer trading system designed for `ERC20` tokens like `wETH`, `wBTC`, and `wSOL`. Sellers can list tokens at their desired price in `USDC`, and buyers can fill them directly on-chain.

    The flow is simple:

    - Sellers lock their tokens and list an order with a price and deadline
    - Buyers purchase tokens by paying the listed `USDc` amount
    - if the order isn't filled before the deadline, sellers can cancel and retrieve their tokens
  
    All orders are tracked using a unique `orderId`, and sellers retain full control over their listings until filled or expired.
  
    Token transfers use `SafeERC20` to ensure secure movement of funds, and the system enforces a strict set of violation rules to prevent misuse.
  
    The contract also supports:
  
    - Amending orders (e.g. changing price or amount)
    - Canceling active or expired orders
    - Emergency withdrawals by the owner (for non-core tokens only)
    - human-readable order infor using `getOrderDetailsString`
  
  - **Features:**
  
    - Fixed-price order creation for selected `ERC20` tokens
    - Secure and gas-efficient architecture
    - Deadline enforcement to prevent stale listings
  
  - **Resources:**
  
    [Order Book](https://www.investopedia.com/terms/o/order-book.asp)
  



## All submissions

### High Risk Findings

H-01. Mitigating Front-Running Vulnerabilities in DeFi[Selected submission](https://codehawks.cyfrin.io/c/2025-07-orderbook/s/cmcnw6vpp0003l804yibbftp7) by [hemantcode](https://profiles.cyfrin.io/u/hemantcode)

H-02. Buy orders can be front-run and edited before being confirmed causing users a loss of funds[Selected submission](https://codehawks.cyfrin.io/c/2025-07-orderbook/s/cmcrv7i1s0003k004m8jix77f) by [chaos304](https://profiles.cyfrin.io/u/chaos304)

### Low Risk Findings

L-01. Protocol Suffers Potential Revenue Leakage due to Precision Loss in Fee Calculation[Selected submission](https://codehawks.cyfrin.io/c/2025-07-orderbook/s/cmcugsp0a0005js041oovkzyb) by [hosam](https://profiles.cyfrin.io/u/hosam)

L-02. Expired Orders Not Cancellable by Anyone (Design Flaw)[Selected submission](https://codehawks.cyfrin.io/c/2025-07-orderbook/s/cmcnfrkpt0003k004fqkue7ho) by [ishwar](https://profiles.cyfrin.io/u/ishwar)

L-03. Missing Event Indexing + Poor dApp Integration[Selected submission](https://codehawks.cyfrin.io/c/2025-07-orderbook/s/cmcnqazui000bk704ae5plij1) by [blee](https://profiles.cyfrin.io/u/blee)

L-04. Inconsistent Order State Management - Expired Orders Remain Active[Selected submission](https://codehawks.cyfrin.io/c/2025-07-orderbook/s/cmco9ekjb0009js046a8fj0fx) by [robertnvt](https://profiles.cyfrin.io/u/robertnvt)

L-05. No Token Transfer Check in emergencyWithdrawERC20[Selected submission](https://codehawks.cyfrin.io/c/2025-07-orderbook/s/cmcpcg9wb0005l504qtguxqka) by [evmninja](https://profiles.cyfrin.io/u/evmninja)

---

## Valid submissions

### H01-No slippage protection in buyOrder

#### Root   + Impact



#### Description

- In normal operation, a buyer reads an order's `amountToSell` and `priceInUSDC` off-chain, and expects to buy that exact amount of tokens at that price.
- However, the seller can call `amendSellOrder()` before `buyOrder()` is executed, modifying `amountToSell` or `priceInUSDC` without buyer consent. This creates a **slippage risk**, where the buyer may overpay or receive fewer tokens than expected.



```soldiity
function buyOrder(uint256 _orderId) public {
        Order storage order = orders[_orderId];
        // Validation checks
        if (order.seller == address(0)) revert OrderNotFound();
        if (!order.isActive) revert OrderNotActive();
        if (block.timestamp >= order.deadlineTimestamp) revert OrderExpired();

        order.isActive = false;
        // @> use of priceInUSDC
        uint256 protocolFee = (order.priceInUSDC * FEE) / PRECISION;
        //  @> use of priceInUSDC
        uint256 sellerReceives = order.priceInUSDC - protocolFee;

        iUSDC.safeTransferFrom(msg.sender, address(this), protocolFee);
		iUSDC.safeTransferFrom(msg.sender, order.seller, sellerReceives);
        //  @>  use of order.amountToSell
        IERC20(order.tokenToSell).safeTransfer(msg.sender, order.amountToSell);

        totalFees += protocolFee;

        emit OrderFilled(_orderId, msg.sender, order.seller);
        }
```



#### Risk

**Likelihood**:

- Sellers can amend their orders at any time before a buyer fills it.
- Buyers relying on off-chain reads cannot guarantee the state hasn’t changed by the time their transaction is mined.

**Impact**:

- Buyer receives fewer tokens than expected, losing value.
- Buyer pays more USDC than intended, enabling a **griefing or front-running** scenario.

#### Proof of Concept

\1) User see the order in the website app ui. For example
"500 wETH against 1000 USDC"

\2) User submits the transaction on-chain through l'UI

\3) While the transaction is on the mempool, the seller changes the amount, for ex. 1 wETH against 1000 USDC"

\4) When the first transaction is taken by a validor, the amount in wETH is now 1. As a result, the user will pay 1000 USDC for only 1 wETH.



#### Recommended Mitigation

Add two supplementary paramters in the function buyOrder: **uint256 expectedAmountToSell, uint256 expectedPriceInUSDC.**

In the function, check if their value match the value inside the order, otherwise revert.

```diff
\+ error SlippageOnAmount();

\+ error SlippageOnPrice();

\- function buyOrder(uint256 _orderId) public { 

\+ function buyOrder(uint256 _orderId, 

+uint256 expectedAmountToSell, uint256 expectedPriceInUSDC) public {  

if (!order.isActive) revert OrderNotActive(); 

\+ if (order.amountToSell != expectedAmountToSell) revert SlippageOnAmount(); 

\+ if (order.priceInUSDC != expectedPriceInUSDC) revert SlippageOnPrice();  

// rest of the code
```



---



## Missed submissions

### Mitigating Front-Running Vulnerabilities in DeFi

#### Root + Impact

#### Description

- Describe the normal behavior in one or more sentences -

  Attackers can exploit the public mempool to front-run amendSellOrder or cancelSellOrder transactions by submitting buyOrder transactions with higher gas prices, buying assets at outdated prices or before cancellation.
  This undermines the seller’s ability to update or cancel orders reliably.

- **Root Cause**:

  Blockchain transactions are visible in the public mempool before confirmation, allowing attackers to observe and outpace **amendSellOrder or cancelSellOrder calls**.
  The contract lacks mechanisms like time-locks or commit-reveal to obscure or delay these actions.

- Explain the specific issue or problem in one or more sentences

// Root cause in the codebase with @> marks to highlight the relevant section

#### Risk

**Likelihood**:

- Reason 1 - High likelihood due to easy mempool monitoring, automated MEV bots, and strong financial incentives in volatile markets.
- Reason 2 - No built-in protections make successful front-running attacks highly probable.

**Impact**:

- Impact 1 - Sellers face financial losses by selling at unintended prices or losing assets they meant to cancel, potentially in the thousands of USDC.
- Impact 2 - User trust and platform reputation suffer, risking reduced adoption and market inefficiency.



#### Recommended Mitigation -



Use time lock mechanism

//updated code 

```
//updated code 
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
​
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";
​
contract OrderBook is Ownable {
    using SafeERC20 for IERC20;
    using Strings for uint256;
​
    struct Order {
        uint256 id;
        address seller;
        address tokenToSell;
        uint256 amountToSell;
        uint256 priceInUSDC;
        uint256 deadlineTimestamp;
        bool isActive;
    }
​
    // --- New State Variables for Time-Lock ---
    struct PendingAmendment {
        uint256 newAmountToSell;
        uint256 newPriceInUSDC;
        uint256 newDeadlineTimestamp;
        uint256 requestTimestamp;
    }
    mapping(uint256 => PendingAmendment) public pendingAmendments;
    mapping(uint256 => uint256) public pendingCancellations;
    uint256 public constant TIME_LOCK_DELAY = 60; // 60 seconds delay
​
    // --- Existing State Variables (unchanged) ---
    uint256 public constant MAX_DEADLINE_DURATION = 3 days;
    uint256 public constant FEE = 3;
    uint256 public constant PRECISION = 100;
    IERC20 public immutable iWETH;
    IERC20 public immutable iWBTC;
    IERC20 public immutable iWSOL;
    IERC20 public immutable iUSDC;
    mapping(address => bool) public allowedSellToken;
    mapping(uint256 => Order) public orders;
    uint256 private _nextOrderId;
    uint256 public totalFees;
​
    // --- Existing Events (unchanged) ---
    event OrderCreated(uint256 indexed orderId, address indexed seller, address indexed tokenToSell, uint256 amountToSell, uint256 priceInUSDC, uint256 deadlineTimestamp);
    event OrderAmended(uint256 indexed orderId, uint256 newAmountToSell, uint256 newPriceInUSDC, uint256 newDeadlineTimestamp);
    event OrderCancelled(uint256 indexed orderId, address indexed seller);
    event OrderFilled(uint256 indexed orderId, address indexed buyer, address indexed seller);
    event TokenAllowed(address indexed token, bool indexed status);
    event EmergencyWithdrawal(address indexed token, uint256 indexed amount, address indexed receiver);
    event FeesWithdrawn(address indexed receiver);
​
    // --- New Events for Time-Lock ---
    event AmendmentRequested(uint256 indexed orderId, uint256 newAmountToSell, uint256 newPriceInUSDC, uint256 newDeadlineTimestamp, uint256 requestTimestamp);
    event CancellationRequested(uint256 indexed orderId, uint256 requestTimestamp);
​
    // --- Existing Errors (unchanged) ---
    error OrderNotFound();
    error NotOrderSeller();
    error OrderNotActive();
    error OrderExpired();
    error OrderAlreadyInactive();
    error InvalidToken();
    error InvalidAmount();
    error InvalidPrice();
    error InvalidDeadline();
    error InvalidAddress();
​
    // --- New Error for Time-Lock ---
    error TimeLockNotElapsed();
​
    // --- Constructor (unchanged) ---
    constructor(address _weth, address _wbtc, address _wsol, address _usdc, address _owner) Ownable(_owner) {
        if (_weth == address(0) || _wbtc == address(0) || _wsol == address(0) || _usdc == address(0)) revert InvalidToken();
        if (_owner == address(0)) revert InvalidAddress();
        iWETH = IERC20(_weth);
        allowedSellToken[_weth] = true;
        iWBTC = IERC20(_wbtc);
        allowedSellToken[_wbtc] = true;
        iWSOL = IERC20(_wsol);
        allowedSellToken[_wsol] = true;
        iUSDC = IERC20(_usdc);
        _nextOrderId = 1;
    }
​
    // --- Modified amendSellOrder: Split into Request and Confirm ---
    function requestAmendSellOrder(
        uint256 _orderId,
        uint256 _newAmountToSell,
        uint256 _newPriceInUSDC,
        uint256 _newDeadlineDuration
    ) external {
        Order storage order = orders[_orderId];
        if (order.seller == address(0)) revert OrderNotFound();
        if (order.seller != msg.sender) revert NotOrderSeller();
        if (!order.isActive) revert OrderAlreadyInactive();
        if (block.timestamp >= order.deadlineTimestamp) revert OrderExpired();
        if (_newAmountToSell == 0) revert InvalidAmount();
        if (_newPriceInUSDC == 0) revert InvalidPrice();
        if (_newDeadlineDuration == 0 || _newDeadlineDuration > MAX_DEADLINE_DURATION) revert InvalidDeadline();
​
        uint256 newDeadlineTimestamp = block.timestamp + _newDeadlineDuration;
        pendingAmendments[_orderId] = PendingAmendment({
            newAmountToSell: _newAmountToSell,
            newPriceInUSDC: _newPriceInUSDC,
            newDeadlineTimestamp: newDeadlineTimestamp,
            requestTimestamp: block.timestamp
        });
​
        emit AmendmentRequested(_orderId, _newAmountToSell, _newPriceInUSDC, newDeadlineTimestamp, block.timestamp);
    }
​
    function confirmAmendSellOrder(uint256 _orderId) external {
        Order storage order = orders[_orderId];
        PendingAmendment memory amendment = pendingAmendments[_orderId];
        if (order.seller == address(0)) revert OrderNotFound();
        if (order.seller != msg.sender) revert NotOrderSeller();
        if (amendment.requestTimestamp == 0) revert("No pending amendment");
        if (block.timestamp < amendment.requestTimestamp + TIME_LOCK_DELAY) revert TimeLockNotElapsed();
        if (!order.isActive) revert OrderAlreadyInactive();
        if (block.timestamp >= order.deadlineTimestamp) revert OrderExpired();
​
        IERC20 token = IERC20(order.tokenToSell);
        if (amendment.newAmountToSell > order.amountToSell) {
            uint256 diff = amendment.newAmountToSell - order.amountToSell;
            token.safeTransferFrom(msg.sender, address(this), diff);
        } else if (amendment.newAmountToSell < order.amountToSell) {
            uint256 diff = order.amountToSell - amendment.newAmountToSell;
            token.safeTransfer(order.seller, diff);
        }
​
        order.amountToSell = amendment.newAmountToSell;
        order.priceInUSDC = amendment.newPriceInUSDC;
        order.deadlineTimestamp = amendment.newDeadlineTimestamp;
​
        // Clear pending amendment
        delete pendingAmendments[_orderId];
​
        emit OrderAmended(_orderId, amendment.newAmountToSell, amendment.newPriceInUSDC, amendment.newDeadlineTimestamp);
    }
​
    // --- Modified cancelSellOrder: Split into Request and Confirm ---
    function requestCancelSellOrder(uint256 _orderId) external {
        Order storage order = orders[_orderId];
        if (order.seller == address(0)) revert OrderNotFound();
        if (order.seller != msg.sender) revert NotOrderSeller();
        if (!order.isActive) revert OrderAlreadyInactive();
        pendingCancellations[_orderId] = block.timestamp;
​
        emit CancellationRequested(_orderId, block.timestamp);
    }
​
    function confirmCancelSellOrder(uint256 _orderId) external {
        Order storage order = orders[_orderId];
        if (order.seller == address(0)) revert OrderNotFound();
        if (order.seller != msg.sender) revert NotOrderSeller();
        if (pendingCancellations[_orderId] == 0) revert("No pending cancellation");
        if (block.timestamp < pendingCancellations[_orderId] + TIME_LOCK_DELAY) revert TimeLockNotElapsed();
        if (!order.isActive) revert OrderAlreadyInactive();
​
        order.isActive = false;
        IERC20(order.tokenToSell).safeTransfer(order.seller, order.amountToSell);
​
        // Clear pending cancellation
        delete pendingCancellations[_orderId];
​
        emit OrderCancelled(_orderId, order.seller);
    }
​
    // --- Modified buyOrder to Prevent Buying Pending Orders ---
    function buyOrder(uint256 _orderId) public {
        Order storage order = orders[_orderId];
        if (order.seller == address(0)) revert OrderNotFound();
        if (!order.isActive) revert OrderNotActive();
        if (block.timestamp >= order.deadlineTimestamp) revert OrderExpired();
        // Check for pending amendment or cancellation
        if (pendingAmendments[_orderId].requestTimestamp != 0 || pendingCancellations[_orderId] != 0) {
            revert("Order has pending amendment or cancellation");
        }
​
        order.isActive = false;
        uint256 protocolFee = (order.priceInUSDC * FEE) / PRECISION;
        uint256 sellerReceives = order.priceInUSDC - protocolFee;
​
        iUSDC.safeTransferFrom(msg.sender, address(this), protocolFee);
        iUSDC.safeTransferFrom(msg.sender, order.seller, sellerReceives);
        IERC20(order.tokenToSell).safeTransfer(msg.sender, order.amountToSell);
​
        totalFees += protocolFee;
​
        emit OrderFilled(_orderId, msg.sender, order.seller);
    }
​
    // --- Other Functions (Unchanged) ---
    // Include createSellOrder, getOrder, getOrderDetailsString, setAllowedSellToken, emergencyWithdrawERC20, withdrawFees as in the original contract
}
```

### Low

#### List

- L-01. Protocol Suffers Potential Revenue Leakage due to Precision Loss in Fee Calculation[Selected submission](https://codehawks.cyfrin.io/c/2025-07-orderbook/s/cmcugsp0a0005js041oovkzyb) by [hosam](https://profiles.cyfrin.io/u/hosam)

- L-02. Expired Orders Not Cancellable by Anyone (Design Flaw)[Selected submission](https://codehawks.cyfrin.io/c/2025-07-orderbook/s/cmcnfrkpt0003k004fqkue7ho) by [ishwar](https://profiles.cyfrin.io/u/ishwar)

- L-03. Missing Event Indexing + Poor dApp Integration[Selected submission](https://codehawks.cyfrin.io/c/2025-07-orderbook/s/cmcnqazui000bk704ae5plij1) by [blee](https://profiles.cyfrin.io/u/blee)

- L-04. Inconsistent Order State Management - Expired Orders Remain Active[Selected submission](https://codehawks.cyfrin.io/c/2025-07-orderbook/s/cmco9ekjb0009js046a8fj0fx) by [robertnvt](https://profiles.cyfrin.io/u/robertnvt)

- L-05. No Token Transfer Check in emergencyWithdrawERC20





#### Protocol Suffers Potential Revenue Leakage due to Precision Loss in Fee Calculation

##### Summary

The protocol's fee calculation, which uses integer division with low precision (`/ 100`), creates a rounding error that can be exploited. For any trade priced at 33 wei of USDC or less, the calculated 3% fee rounds down to zero, allowing the trade to be processed fee-free. While the high gas cost of performing many small transactions makes a large-scale economic attack impractical today, this represents a fundamental design flaw that causes a **verifiable and permanent leakage of protocol revenue**. This flaw undermines the economic model and should be remediated as a matter of protocol robustness and best practice.

##### Finding Description

The `buyOrder` function calculates the protocol fee using the formula `(order.priceInUSDC * 3) / 100`. Due to Solidity's integer division, any result with a remainder is truncated. Consequently, if the numerator `(order.priceInUSDC * 3)` is less than `100`, the resulting `protocolFee` is `0`. This is true for any `priceInUSDC` value between 1 and 33.

```solidity
// src/OrderBook.sol:203

uint256 protocolFee = (order.priceInUSDC * FEE) / PRECISION; // FEE = 3, PRECISION = 100
```

This creates a scenario where users can intentionally price their orders just below the 34 wei threshold to avoid fees. Although a single such transaction has a negligible impact, it establishes a pattern of value leakage that is built into the protocol's core logic.

##### Impact

The primary impact is a **direct, albeit small, loss of protocol revenue on certain trades**. While the economic viability of a large-scale attack is questionable due to gas costs, the existence of this flaw has several negative consequences:

- **Protocol Value Leak:** The protocol fails to capture fees it is entitled to, creating a small but persistent drain on its treasury.
- **Design Flaw:** It demonstrates a weakness in the handling of financial calculations. In DeFi, even minor rounding errors can be aggregated or combined with other exploits to cause significant issues.
- **Future Risk:** A reduction in L2 gas fees or the introduction of new protocol features could potentially make this exploit more economically viable in the future.

##### Likelihood

**Medium.** From a technical standpoint, the flaw is easy to trigger. Any user can create a low-priced order. However, the economic incentive to do so at scale is currently low, which reduces the practical likelihood of a major exploit.

##### Proof of Concept

The following test demonstrates that an order priced at 33 wei of USDC results in zero fees being collected by the protocol, confirming the rounding vulnerability.

**Test File:** `test/FeeRoundingVulnerabilityV2.t.sol`

```solidity

// SPDX-License-Identifier: SEE LICENSE IN LICENSE
pragma solidity ^0.8.0;
​
import {Test, console2} from "forge-std/Test.sol";
import {OrderBook} from "../src/OrderBook.sol";
import {MockUSDC} from "./mocks/MockUSDC.sol";
import {MockWETH} from "./mocks/MockWETH.sol";
​
/**
 * @title Fee Rounding Vulnerability PoC
 * @notice Demonstrates how integer division in fee calculations leads to revenue loss for the protocol.
 */
contract FeeRoundingExploitTest is Test {
    OrderBook book;
    MockWETH weth;
    MockUSDC usdc;
​
    address owner = makeAddr("owner");
    address seller = makeAddr("seller");
    address buyer = makeAddr("buyer");
​
    function setUp() public {
        weth = new MockWETH(18);
        usdc = new MockUSDC(6);
        
        vm.prank(owner);
        book = new OrderBook(address(weth), address(weth), address(weth), address(usdc), owner);
​
        // Mint tokens to participants
        weth.mint(seller, 10e18); // 10 WETH for multiple orders
        usdc.mint(buyer, 1000e6); // 1000 USDC
    }
​
    /// @notice This test proves that a single order with a low price (e.g., 33 wei of USDC)
    ///         results in a calculated fee of zero, allowing a trade to occur fee-free.
    function test_PoC_SingleOrderFeeEvasion() public {
        // A price of 33 will result in a fee calculation of (33 * 3) / 100, which rounds down to 0.
        uint256 exploitablePrice = 33;
        
        // --- Execution ---
        vm.startPrank(seller);
        weth.approve(address(book), 1e18);
        uint256 orderId = book.createSellOrder(address(weth), 1e18, exploitablePrice, 1 days);
        vm.stopPrank();
​
        uint256 feesBefore = book.totalFees();
        assertEq(feesBefore, 0, "Initial fees should be zero");
​
        vm.startPrank(buyer);
        usdc.approve(address(book), exploitablePrice);
        book.buyOrder(orderId);
        vm.stopPrank();
​
        // --- Assertion ---
        uint256 feesAfter = book.totalFees();
        console2.log("Price per order:", exploitablePrice);
        console2.log("Protocol fees collected for this trade:", feesAfter - feesBefore);
​
        // The key assertion: The protocol failed to collect any fee for this transaction.
        assertEq(feesAfter, 0, "VULNERABILITY: Protocol should have collected a fee, but it rounded down to zero.");
    }
​
    /// @notice This test demonstrates how an attacker can exploit the rounding error repeatedly
    ///         by splitting a large sale into multiple small, fee-free orders, causing
    ///         a cumulative loss of revenue for the protocol.
    function test_PoC_CumulativeFeeLoss() public {
        uint256 numOrders = 20;
        uint256 exploitablePrice = 33; // This price results in a fee of 0
        
        // --- Execution ---
        for (uint256 i = 0; i < numOrders; i++) {
            vm.startPrank(seller);
            weth.approve(address(book), 1e17); // Sell 0.1 WETH per order
            uint256 orderId = book.createSellOrder(address(weth), 1e17, exploitablePrice, 1 days);
            vm.stopPrank();
​
            vm.startPrank(buyer);
            usdc.approve(address(book), exploitablePrice);
            book.buyOrder(orderId);
            vm.stopPrank();
        }
​
        // --- Assertion ---
        uint256 totalFeesCollected = book.totalFees();
        
        console2.log("Number of fee-free orders processed:", numOrders);
        console2.log("Total fees collected by protocol:", totalFeesCollected);
​
        // The key assertion: After 20 trades, the protocol has still earned nothing.
        assertEq(totalFeesCollected, 0, "VULNERABILITY: Protocol revenue remains zero after multiple trades due to rounding exploit.");
    }
}
```



**Successful Test Output:**

[PASS] test_PoC_SingleOrderFeeEvasion()

Logs:

  Price per order: 33

  Protocol fees collected for this trade: 0

The successful test confirms that it is possible to execute a trade without paying any fees, validating the existence of the revenue leakage flaw.

##### Recommended Mitigation

The standard industry practice to prevent such rounding issues is to increase the precision of the calculation by using basis points (1 bp = 0.01%).

```diff
// src/OrderBook.sol



\-    uint256 public constant FEE = 3; // 3%

\-    uint256 public constant PRECISION = 100;

\+    uint256 public constant FEE = 300; // 300 bps = 3.00%

\+    uint256 public constant PRECISION = 10000; // Represents 100.00%
```

**Impact of the Fix:**
With this change, the fee calculation becomes significantly more precise. While a price of 33 wei would still result in a zero fee (`(33 * 300) / 10000 = 0`), the threshold for earning a fee is much lower. For a more realistic low-value transaction of **1 USDC (1,000,000 wei)**, the fee would be:
`(1,000,000 * 300) / 10000 = 30,000 wei` (or 0.03 USDC).
This ensures that fees are collected fairly and consistently across almost all non-trivial trades, patching the revenue leak.
