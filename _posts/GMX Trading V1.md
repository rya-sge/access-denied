# GMX Trading V1

GMX is a decentralized crypto exchange allowing trading .

To use the platform, you don't need for a username or password but instead will use a compatible crypto wallet (e.g [Rabby](https://rabby.io/ Wallet)

The platform uses a price feed based on an aggregate of exchanges which reduces the risk of liquidations from temporary wicks.

The two supported blockchains are Arbitrum or Avalance, so you need  to have ETH in your Arbitrum account or AVAX in your Avalanche account to start trading.

## Swaps

[https://docs.gmx.io/docs/trading/v1#swaps](https://docs.gmx.io/docs/trading/v1#swaps)

GMX supports both swaps and leverage trading. 

For leverage trading, please see the below sections for more information.

## Opening a Position

https://docs.gmx.io/docs/trading/v1#opening-a-position

Long position:

- Earns a profit if the token's price goes up
- Makes a loss if the token's price goes down

Short position:

- Earns a profit if the token's price goes down
- Makes a loss if the token's price goes up

After selecting your side, key in the amount you want to pay and the leverage you want to use.

Below the swap box you would see the "Exit Price", which is the price that is used to calculate profits if you open and then immediately close a position. The exit price will change with the price of the token you are longing or shorting.

### Fees

The trading fee to open a position is 0.1% of the position size, similarly there is a 0.1% fee when closing the position.

There is also a "Borrow Fee" that is deducted at the start of every hour. This is the fee paid to the counter-party of your trade. The fee per hour will vary based on utilization, it is calculated as (assets borrowed) / (total assets in pool) * 0.01%. The "Borrow Fee" for longing or shorting is shown below the swap box.

### Slippage

While there are no price impacts for trades, there can be slippage due to price movements between when your trade transaction is submitted and when it is confirmed on the blockchain. Slippage is the difference between the expected price of the trade and the execution price, this can be customised in the "Settings" menu by clicking on the "..." icon at the top right of the page.

## Managing Positions

[docs.gmx.io/docs/trading/v1#managing-positions](https://docs.gmx.io/docs/trading/v1#managing-positions)

After opening a trade, you would be able to view it under your Positions list, you can also click on "Edit" to deposit or withdraw collateral, this allows you to manage your leverage and liquidation price.

When you open a position or deposit collateral, a snapshot of the USD price of your collateral is taken, so e.g. if your collateral is 0.1 ETH and the price of ETH is 5000 USD at the time, then your collateral is 500 USD and will not change even if the price of ETH changes.

The amount of profit and loss you make will be proportional to your position size. 

### Long Position

For example, if you open a long ETH position of size 10,000 USD

- If the price of ETH increases by 10%, the position would have a profit of 1000 USD
-  If the price of ETH decreases by 10%, the position would have a loss of 1000 USD.

### Short position

If a short position was opened instead, then:

- if the price of ETH decreased by 10% the position would have a profit of 1000 USD
- if the price of ETH increased by 10%, the position would have a loss of 1000 USD.

Leverage for a position is displayed as (position size) / (position collateral). 

If you'd like to display the leverage as (position size + PnL) / (position collateral) instead, you can customise this in the "Settings" menu by clicking on the "..." icon at the top right of the page.

Note that when depositing collateral into a long position, there is a 0.3% deposit fee for the conversion of the asset to its USD value, e.g. ETH amount to USD value. This is to prevent deposits from being used as a zero fee swap. This does not apply to shorts. This fee also does not apply when withdrawing collateral for longs or shorts.

## Closing a Position

[docs.gmx.iov1#closing-a-position](https://docs.gmx.io/docs/trading/v1#closing-a-position)

You can close a position partially or completely by clicking on the "Close" button in the position row.

For long positions, profits are paid in the asset you are longing, e.g. if you long ETH you would get your profits as ETH.

For short positions, profits will be paid out in the same stablecoin that you used to open the position, e.g. USDC or USDT.

You can customize the token to be received by changing the "Receive" token in the "Close Position" menu. Note that this may perform a swap from your profit token to the token you select if needed, the swap fees will be shown in the "Close Position" menu.

## Stop-Loss / Take-Profit Orders[

[docs.gmx.io/v1#stop-loss--take-profit-orders](https://docs.gmx.io/docs/trading/v1#stop-loss--take-profit-orders)

You can set stop-loss and take-profit orders by clicking on the "Close" button and selecting the "Trigger" tab.

After creating a trigger order, it will appear in your position's row as well as under the "Orders" tab, you can edit the order and change the trigger price if needed.

If you close a position manually, the associated trigger orders will remain open, you would need to cancel them manually if you do not want the order to be active when opening future positions.

Note that orders are not guaranteed to execute, this can occur in a few situations including but not exclusive to:

- The mark price which is an aggregate of exchange prices did not reach the specified price
- The specified price was reached but not long enough for it to be executed
- The order's size exceeds the remaining position size
- No keeper picked up the order for execution

Additionally, trigger orders are market orders and are not guaranteed to execute at the trigger price.

## Liquidations

[docs.gmx.io/v1#liquidations](https://docs.gmx.io/docs/trading/v1#liquidations)

If an ETH long position is opened and the position size is larger than the collateral value, then there would be a price at which the position's loss amount is very close to the collateral value.

This is referred to as the Liquidation Price and is calculated as the price at which the (collateral - losses - borrow fee) is less than 1% of your position's size. If the token's price crosses this point then the position will be automatically closed.

Due to the borrow fee your liquidation price will change over time, especially if you use a leverage that is more than 10x and have the position open for more than a few days, so it is important to monitor your liquidation price.

Collateral can be deposited using the "Edit" button in the position row, this will help to improve the liquidation price and reduce the risk of liquidation.

When a position is liquidated, any collateral remaining after deducting losses and fees would be returned to your account.

## Pricing

[docs.gmx.io/v1#pricing](https://docs.gmx.io/docs/trading/v1#pricing)

There is no price impact for trades on GMX V1, so you can execute large trades exactly at the mark price. During times of high volatility there may be a spread from the Chainlink price to the median price of reference exchanges.

The mark prices are displayed next to the market name, long positions will be opened at the higher price and closed at the lower price while short positions will be opened at the lower price and closed at the higher price.

The chart will indicate the average of the two mark prices.

## Fees

[docs.gmx.io/docs/trading/v1#fees](https://docs.gmx.io/docs/trading/v1#fees)

The cost to open / close a position is 0.1% of the position size.

The collateral of long positions is the token being longed, for ETH longs the collateral is ETH and for BTC longs the collateral is WBTC, etc.

The collateral of shorts positions is any of the supported stablecoins e.g. USDC, USDT, DAI, FRAX.

If a swap is needed when opening or closing a position then the regular swap fee would apply, this fee is 0.2% to 0.8% of the collateral size, the exact fee depends on whether the swap improves balance or reduces it.

There is also a network fee detailed below, which is used to pay for the blockchain network costs.

## Network Fee

[docs.gmx.io/v1#network-fee](https://docs.gmx.io/docs/trading/v1#network-fee)

There are two transactions involved in opening / closing / editing a position:

- User sends the first transaction to request open / close / deposit collateral / withdraw collateral
- Keepers observe the blockchain for these requests then execute them

The cost of the second transaction is displayed in the interface as the "Network Fee". This network cost is paid to the blockchain network.

## Stablecoin Pricing

[docs.gmx.io/v1#stablecoin-pricing](https://docs.gmx.io/docs/trading/v1#stablecoin-pricing)

In case the price of a stablecoin depegs from 1 USD:

- Opening and closing short positions during this time would incur a cost on the collateral based on a spread of 1 USD to the Chainlink price of the stablecoin. For example, if the price of the chosen stablecoin depegs to 0.95 USD, opening a position using 1000 of that stablecoin would result in a position collateral of 950 USD based on a price of 0.95 USD, when closing the position, 950 of the stablecoin would be withdrawn based on a price of 1 USD, this is to prevent front-running issues during a depeg since collateral is stored as a USD value and converted to tokens based on the latest price.
- To ensure that profits for all short positions can always be fully paid out, the contracts will pay out profits in the stablecoin based on a price of 1 USD or the current Chainlink price for the stablecoin, whichever is higher.
- For swaps using the depegged stablecoin, the spread from 1 USD to the Chainlink price of the stablecoin will similarly apply.
- Long positions should not be affected though there may be a spread if swapping from a depegged stablecoin into the long collateral needed for the position, e.g. to long ETH, ETH collateral is needed. Alternative swap platforms could be used to execute the swap before opening the long position. The interface should show a warning if there is a large spread for this.