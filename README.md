# SNW Games Automations
<div><b>SQUID.py</b> - SNW Main (SQUID) Game Tools (Play Cycle, Buy Contracts).</div>
<div><b>Workers.py</b> - SNW Workers (STAFF) Game Tools (Check, Claim, Buy and others).</div>
<div><b>Tools.py</b> - Approves for SNW & Biswap HP Contracts, Deposits to Biswap HP and others.</div>
<div><b>The interactions takes places directly with the contracts of the games.</b></div>
<h2>Description</h2>
<h3>SQUID.py</h3>
<div><b>SQUID.py - 1. Buy new Contracts for Players!</b>
<div>This feature allows you to purchase new players at a scheduled time.</div><br/>
</div>
<div><b>SQUID.py - 2. Run Play Game cycle!</b>
<div>This feature allows you to run cycle with checking opportunity to play game and then play game if available.</div>
</div>

<h3>Workers.py</h3>
<div><b>Workers.py - 1. Checking workers Statistic!</b>
<div>This feature allows you to check every worker statistic. There is statistic with details and without. Detailed statistic will show every parameter of every worker in your wallets. Custom statistic will show you only amount of available to buy and to claim workers.</div><br/>
</div>
<div><b>Workers.py - 2. Claiming Available Workers!</b>
<div>This feature allows you to claim every worker that has finished work.</div><br/>
</div>
<div><b>Workers.py - 3. Hiring New Players!</b>
<div>This feature allows you to hire new workers for every wallet of your seed phrase.</div><br/>
</div>
<div><b>Workers.py - 4. Use Another Mnemonic!</b>
<div>This feature allows you to change current seed phrase.</div><br/>
</div>
<div><b>Workers.py - 5. One Worker per one Wallet! (Yes/No)</b>
<div>This feature allows you to buy only one worker per one wallet. There is two workers per one wallet available but due to high demand there is no reason to try buying two workers.</div><br/>
</div>
<div><b>Workers.py - 6. Using Priority Fees! (Yes/No)</b>
<div>This feature allows you to use priority fees for BSC. This function was added due to high demand of game.</div>
</div>
<h3>Tools.py</h3>
<div><b>Tools.py - 1. Approve HP!</b>
<div>This feature allows you to approve permission for every wallet for Holder Pool contract. You need to do it if you want to make deposit to this contract.</div><br/>
</div>
<div><b>Tools.py - 2. Approve SNW!</b>
<div>This feature allows you to approve permission for every wallet for SNW Game contract. You need to do it if you want to have opportunity for playing this contract game.</div><br/>
</div>
<div><b>Tools.py - 3. Deposit to HP!</b>
<div>This feature allows you to deposit any amount of tokens to Holder Pool contract. This is condition for playing games.</div><br/>
</div>
<div><b>Tools.py - 4. Withdraw from HP!</b>
<div>This feature allows you to withdraw all your tokens from Holder Pool if you do not want to play more.</div><br/>
</div>
<div><b>Tools.py - 5. Show wallets Balances!</b>
<div>This feature allows you to check balances of your wallets.</div><br/>
</div>
<div><b>Tools.py - 6. Collecting BSW Tokens!</b>
<div>This feature allows you to get BSW tokens from all your wallets to one main wallet.</div><br/>
</div>
<div><b>Tools.py - 7. Use Another Mnemonic!</b>
<div>This feature allows you to change current seed phrase.</div><br/>
</div>
<h2>Usage</h2>
<div>To use any script run it via python3 and follow the menu functions!</div>
<h2>Dependencies</h2>
<div>You need to install some python3 libraries: <b>pip3 install web3, requests, json, getpass, threading</b></div>
<div>
<h2>Additionally</h2>
<div><b>crypto.py</b> - Library for Extracting Private Keys from Mnemonic (<a href="https://github.com/michailbrynard/ethereum-bip44-python" target="_blank">michailbrynard/ethereum-bip44-python</a>).</div>
<div><b>LICENSE</b> for <b>crypto.py</b> - (<a href="https://github.com/michailbrynard/ethereum-bip44-python/blob/master/LICENSE" target="_blank">michailbrynard/ethereum-bip44-python/blob/master/LICENSE</a>).</div>