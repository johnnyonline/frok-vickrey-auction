import ape
import hexbytes
# from brownie import ZERO_ADDRESS, accounts, history, web3
# from eth_abi import encode
# from eth_account import Account
# from eth_account.messages import encode_defunct

# Some helper functions


def _ensureToken(token, token_id, owner):
    # XXX Make sure that token does not yet exist
    stop_mint = False
    i = 0
    while stop_mint is False:
        _mint(token, owner)
        try:
            if token.ownerOf(token_id) == owner:
                stop_mint = True
        except Exception:
            stop_mint = False
        if i > 10:
            # assert False
            break
        i += 1


def _mint(token, deployer):
    token.mint(sender=deployer)


def _ensureNotToken(token, tokenID):
    with ape.reverts():
        token.ownerOf(tokenID)


#
# Verify that a Transfer event has been logged
#
def _verifyTransferEvent(txn_receipt, _from, to, tokenID):
    event = ape.project.Frok.Transfer.from_receipt(txn_receipt)[0]
    assert event._tokenId == tokenID
    assert event._from == _from
    assert event._to == to


# #
# # Verify that an Approval event has been logged
# #
# def _verifyApprovalEvent(txn_receipt, owner, spender, tokenID):
#     event = txn_receipt.events["Approval"]
#     assert event["_tokenId"] == tokenID
#     assert event["_owner"] == owner
#     assert event["_approved"] == spender


# #
# # Verify that an ApprovalForAll event has been logged
# #
# def _verifyApprovalForAllEvent(txn_receipt, owner, operator, approved):
#     event = txn_receipt.events["ApprovalForAll"]
#     assert event["_owner"] == owner
#     assert event["_operator"] == operator
#     assert event["_approved"] == approved


# def signAllowlistMint(deployer, minter, amount):
#     alice_encoded = encode(["string", "address", "uint256"], ["allowlist:", minter.address, amount])
#     alice_hashed = web3.keccak(alice_encoded)
#     alice_signable_message = encode_defunct(alice_hashed)
#     signed_message = Account.sign_message(alice_signable_message, deployer.private_key)
#     return signed_message


# #
# # Inquire the balance for the zero address - this should raise an exception
# #
# def test_balanceOf_zero_address(token):
#     # This should raise an error. Note that we need to provide an address with
#     # 40 hex digits, as otherwise the web3 ABI encoder treats the argument as a string
#     # and is not able to find the matching ABI entry
#     with brownie.reverts():  # "ERC721: balance query for the zero address"):
#         token.balanceOf(ZERO_ADDRESS)


#
# Inquire the balance for a non-zero address
#
def test_balanceOf_nonzero_address(token):
    balance = token.balanceOf("0x1" + "0" * 39)
    assert 0 == balance



def test_mint_not_minter(token, alice):
    with ape.reverts():
        token.mint(sender=alice)


def test_withdraw_only_owner(token, alice, deployer):
    token.mint(sender=deployer)

    with ape.reverts("Caller is not the owner"):
        token.withdraw(sender=alice)



#
# Get owner of non-existing token
#
def test_owner_of_invalid_token_id(token):
    token_id = 20
    _ensureNotToken(token, token_id)
    with ape.reverts():  # "ERC721: owner query for nonexistent token"):
        token.ownerOf(token_id)


#
# Test a valid transfer, initiated by the current owner of the token
#
def test_transferFrom(token, deployer, bob):
    token_id = 1
    _ensureToken(token, token_id, deployer)

    # Remember balances
    old_balance_deployer = token.balanceOf(deployer)
    old_balance_bob = token.balanceOf(bob)

    # Now do the transfer
    txn_receipt = token.transferFrom(deployer, bob, token_id, sender=deployer)

    # check owner of NFT
    assert bob == token.ownerOf(token_id)

    # Check balances
    new_balance_deployer = token.balanceOf(deployer)
    new_balance_bob = token.balanceOf(bob)

    assert new_balance_deployer + 1 == old_balance_deployer
    assert old_balance_bob + 1 == new_balance_bob

    # Verify that an Transfer event has been logged
    _verifyTransferEvent(txn_receipt, deployer, bob, token_id)

# // todo - here
# #
# # Test an invalid transfer - from is not current owner
# #
# def test_transferFrom_not_owner(token, deployer, bob, charlie):
#     token_id = 20
#     _ensureToken(token, token_id, deployer)
#     with brownie.reverts():  # "ERC721: transfer caller is not owner nor approved"):
#         token.transferFrom(charlie, bob, token_id, {"from": charlie})


# #
# # Test an invalid transfer - to is the zero address
# #
# def test_transferFrom_to_zero_zddress(token, deployer):
#     token_id = 20
#     _ensureToken(token, token_id, deployer)
#     with brownie.reverts():  # "ERC721: transfer to the zero address"):
#         token.transferFrom(deployer, ZERO_ADDRESS, token_id, {"from": deployer})


# #
# # Test an invalid transfer - invalid token ID
# #
# def test_transfer_from_invalid_token_id(token, deployer, bob):
#     token_id = token.totalSupply() + 2
#     with brownie.reverts():
#         token.transferFrom(deployer, bob, token_id, {"from": deployer})


# #
# # Test an invalid transfer - not authorized
# #
# def test_transfer_from_not_authorized(token, deployer, bob, charlie):
#     token_id = 20
#     _ensureToken(token, token_id, deployer)
#     with brownie.reverts():  # "ERC721: transfer caller is not owner nor approved"):
#         token.transferFrom(deployer, bob, token_id, {"from": charlie})


# #
# # Test a valid safe transfer, initiated by the current owner of the token
# #
# def test_safe_transfer_from_current_owner(token, deployer, bob):
#     token_id = 20
#     _ensureToken(token, token_id, deployer)

#     # Remember balances
#     old_balance_deployer = token.balanceOf(deployer)
#     old_balance_bob = token.balanceOf(bob)

#     # Now do the transfer
#     txn_receipt = token.safeTransferFrom(
#         deployer, bob, token_id, hexbytes.HexBytes(""), {"from": deployer}
#     )

#     # check owner of NFT
#     assert bob == token.ownerOf(token_id)

#     # Check balances
#     assert token.balanceOf(deployer) + 1 == old_balance_deployer
#     assert old_balance_bob + 1 == token.balanceOf(bob)

#     # Verify that an Transfer event has been logged
#     _verifyTransferEvent(txn_receipt, deployer, bob, token_id)


# #
# # Test an invalid safe transfer - from is not current owner
# #
# def test_safe_transfer_from_not_owner(token, deployer, bob, charlie):
#     token_id = 20
#     _ensureToken(token, token_id, deployer)
#     with brownie.reverts():  # "ERC721: transfer caller is not owner nor approved"):
#         token.safeTransferFrom(charlie, bob, token_id, hexbytes.HexBytes(""), {"from": charlie})


# #
# # Test an safe invalid transfer - to is the zero address
# #
# def test_safe_transfer_from_to_zero_address(token, deployer):
#     token_id = 20
#     _ensureToken(token, token_id, deployer)
#     with brownie.reverts():  # "ERC721: transfer to the zero address"):
#         token.safeTransferFrom(
#             deployer, ZERO_ADDRESS, token_id, hexbytes.HexBytes(""), {"from": deployer}
#         )


# #
# # Test an invalid safe transfer - invalid token ID
# #
# def test_safe_transfer_tid_from_to_zero_address(token, deployer, bob):
#     token_id = 20

#     # Make sure that token does not exist
#     _ensureNotToken(token, token_id)

#     # Now do the transfer
#     with brownie.reverts():
#         token.safeTransferFrom(deployer, bob, token_id, hexbytes.HexBytes(""), {"from": deployer})


# #
# # Test an invalid safe transfer - not authorized
# #
# def test_safe_transfer_from_not_authorized(token, deployer, bob, charlie):
#     token_id = 20
#     _ensureToken(token, token_id, deployer)
#     with brownie.reverts():  # "ERC721: transfer caller is not owner nor approved"):
#         token.safeTransferFrom(deployer, bob, token_id, hexbytes.HexBytes(""), {"from": bob})


# #
# # Test a valid safe transfer to a contract returning the proper magic value
# #
# def test_safe_transfer_from(token, tokenReceiver, deployer):
#     token_receiver = tokenReceiver
#     data = "0x1234"
#     token_id = 20
#     _ensureToken(token, token_id, deployer)

#     # get current invocation count of test contract
#     oldInvocationCount = token_receiver.getInvocationCount()
#     # Remember balances
#     oldBalanceDeployer = token.balanceOf(deployer)
#     oldBalanceToken = token.balanceOf(token_receiver.address)
#     # Make sure that the contract returns the correct magic value
#     token_receiver.setReturnCorrectValue(True)
#     # Now do the transfer
#     txn_receipt = token.safeTransferFrom(
#         deployer, token_receiver.address, token_id, hexbytes.HexBytes(data), {"from": deployer}
#     )
#     # check owner of NFT
#     assert token_receiver.address == token.ownerOf(token_id)
#     # Check balances
#     newBalanceDeployer = token.balanceOf(deployer)
#     newBalanceToken = token.balanceOf(token_receiver.address)
#     assert newBalanceDeployer + 1 == oldBalanceDeployer
#     assert oldBalanceToken + 1 == newBalanceToken
#     # get current invocation count of test contract
#     newInvocationCount = token_receiver.getInvocationCount()
#     assert oldInvocationCount + 1 == newInvocationCount
#     # Check that data has been stored
#     assert token_receiver.getData() == data
#     # Verify that an Transfer event has been logged
#     _verifyTransferEvent(txn_receipt, deployer, token_receiver.address, token_id)


# #
# # Test a valid safe transfer to a contract returning the wrong proper magic value
# #
# def test_safeTransferFrom_wrongMagicValue(token, tokenReceiver, deployer):
#     tokenID = 20
#     _ensureToken(token, tokenID, deployer)
#     # Make sure that the contract returns the wrong magic value
#     tokenReceiver.setReturnCorrectValue(False)
#     # Now do the transfer
#     with brownie.reverts():  # "Did not return magic value"):
#         token.safeTransferFrom(
#             deployer, tokenReceiver.address, tokenID, hexbytes.HexBytes(""), {"from": deployer}
#         )
#     # Reset behaviour of test contract
#     tokenReceiver.setReturnCorrectValue(True)


# #
# # Test a valid safe transfer to a contract returning the proper magic value - no data
# #
# def test_safeTransferFrom_noData(token, tokenReceiver, deployer):
#     tokenID = 20
#     _ensureToken(token, tokenID, deployer)
#     # get current invocation count of test contract
#     oldInvocationCount = tokenReceiver.getInvocationCount()
#     # Remember balances
#     oldBalanceDeployer = token.balanceOf(deployer)
#     oldBalanceToken = token.balanceOf(tokenReceiver.address)
#     # Make sure that the contract returns the correct magic value
#     tokenReceiver.setReturnCorrectValue(True)
#     # Now do the transfer
#     txn_receipt = token.safeTransferFrom(
#         deployer, tokenReceiver.address, tokenID, {"from": deployer}
#     )
#     # check owner of NFT
#     assert tokenReceiver.address == token.ownerOf(tokenID)
#     # Check balances
#     newBalanceDeployer = token.balanceOf(deployer)
#     newBalanceToken = token.balanceOf(tokenReceiver.address)
#     assert newBalanceDeployer + 1 == oldBalanceDeployer
#     assert oldBalanceToken + 1 == newBalanceToken
#     # get current invocation count of test contract
#     newInvocationCount = tokenReceiver.getInvocationCount()
#     assert oldInvocationCount + 1 == newInvocationCount
#     # Verify that an Transfer event has been logged
#     _verifyTransferEvent(txn_receipt, deployer, tokenReceiver.address, tokenID)


# #
# # Test an approval which is not authorized
# #
# def test_approval_not_authorized(token, deployer, bob):
#     token_id = 20
#     _ensureToken(token, token_id, deployer)
#     with brownie.reverts():  # "ERC721: approve caller is not owner nor approved for all"):
#         token.approve(deployer, token_id, {"from": deployer})


# #
# # Test a valid transfer, initiated by an approved sender
# #
# def test_transfer_from_approved(token, deployer, bob, charlie):
#     token_id = 20
#     _ensureToken(token, token_id, deployer)

#     # Approve
#     token.approve(charlie, token_id, {"from": deployer})
#     old_balance_deployer = token.balanceOf(deployer)
#     old_balance_bob = token.balanceOf(bob)

#     # Now do the transfer
#     txn_receipt = token.transferFrom(deployer, bob, token_id, {"from": charlie})
#     assert bob == token.ownerOf(token_id)

#     # Check balances
#     new_balance_deployer = token.balanceOf(deployer)
#     new_balance_bob = token.balanceOf(bob)
#     assert new_balance_deployer + 1 == old_balance_deployer
#     assert old_balance_bob + 1 == new_balance_bob

#     # Verify that an Transfer event has been logged
#     _verifyTransferEvent(txn_receipt, deployer, bob, token_id)


# #
# # Test setting and getting approval
# #
# def test_approval(token, deployer, bob, charlie):
#     token_id = 20

#     # Make sure that token does not yet exist
#     _ensureNotToken(token, token_id)

#     # Get approval - should raise
#     with brownie.reverts():  # "ERC721: approved query for nonexistent token"):
#         token.getApproved(token_id)

#     # Approve - should raise
#     with brownie.reverts():  # "ERC721: owner query for nonexistent token"):
#         token.approve(charlie, token_id, {"from": deployer})

#     # Mint
#     _mint(token, deployer)

#     # Approve for charlie
#     txn_receipt = token.approve(charlie, token_id, {"from": deployer})

#     # Check
#     assert charlie == token.getApproved(token_id)

#     # Verify events
#     _verifyApprovalEvent(txn_receipt, deployer, charlie, token_id)


# #
# # Test that approval is reset to zero address if token is transferred
# #
# def test_approval_resetUponTransfer(token, deployer):
#     alice = accounts[1]
#     bob = accounts[2]
#     tokenID = 20
#     _ensureToken(token, tokenID, deployer)
#     # Approve for bob
#     token.approve(bob, tokenID, {"from": deployer})
#     # Check
#     assert bob == token.getApproved(tokenID)
#     # Do transfer
#     token.transferFrom(deployer, alice, tokenID, {"from": bob})
#     # Check that approval has been reset
#     assert ("0x" + 40 * "0") == token.getApproved(tokenID)


# #
# # Test setting and clearing the operator flag
# #
# def test_setGetOperator(token):
#     me = accounts[0]
#     alice = accounts[1]
#     bob = accounts[2]
#     assert not token.isApprovedForAll(me, bob)
#     assert not token.isApprovedForAll(me, alice)
#     # Declare bob as operator for me
#     txn_receipt = token.setApprovalForAll(bob, True, {"from": me})
#     # Check
#     assert token.isApprovedForAll(me, bob)
#     assert not token.isApprovedForAll(me, alice)
#     # Check events
#     _verifyApprovalForAllEvent(txn_receipt, me, bob, True)
#     # Do the same for alice
#     txn_receipt = token.setApprovalForAll(alice, True, {"from": me})
#     # Check
#     assert token.isApprovedForAll(me, bob)
#     assert token.isApprovedForAll(me, alice)
#     # Check events
#     _verifyApprovalForAllEvent(txn_receipt, me, alice, True)
#     # Reset both
#     txn_receipt = token.setApprovalForAll(bob, False, {"from": me})
#     # Check events
#     _verifyApprovalForAllEvent(txn_receipt, me, bob, False)
#     txn_receipt = token.setApprovalForAll(alice, False, {"from": me})
#     # Check events
#     _verifyApprovalForAllEvent(txn_receipt, me, alice, False)
#     # Check
#     assert not token.isApprovedForAll(me, bob)
#     assert not token.isApprovedForAll(me, alice)


# def test_only_approval_not_on_my_tokens(token, alice):
#     with brownie.reverts():
#         token.setApprovalForAll(alice, True, {"from": alice})


# #
# # Test authorization logic for setting and getting approval
# #
# def test_approval_authorization(token, deployer, bob, charlie):
#     token_id = 20
#     _ensureToken(token, token_id, deployer)
#     # Try to approve for charlie while not being owner or operator - this should raise an exception
#     with brownie.reverts():  # "ERC721: approve caller is not owner nor approved for all"):
#         token.approve(charlie, token_id, {"from": bob})

#     # Now make bob an operator for alice
#     token.setApprovalForAll(bob, True, {"from": deployer})

#     # Approve for charlie again - this should now work
#     txn_receipt = token.approve(charlie, token_id, {"from": bob})

#     # Check
#     assert charlie == token.getApproved(token_id)
#     _verifyApprovalEvent(txn_receipt, deployer, charlie, token_id)

#     # Reset
#     token.setApprovalForAll(bob, False, {"from": deployer})


# #
# # Test a valid transfer, initiated by an operator for the current owner of the token
# #
# def test_transferFrom_operator(token, deployer):
#     alice = accounts[1]
#     bob = accounts[2]
#     tokenID = 20
#     _ensureToken(token, tokenID, deployer)
#     # Now make bob an operator for me
#     token.setApprovalForAll(bob, True, {"from": deployer})
#     # Remember balances
#     oldBalanceDeployer = token.balanceOf(deployer)
#     oldBalanceAlice = token.balanceOf(alice)
#     # Now do the transfer
#     txn_receipt = token.transferFrom(deployer, alice, tokenID, {"from": bob})
#     # Reset
#     token.setApprovalForAll(bob, False, {"from": deployer})
#     # check owner of NFT
#     assert alice == token.ownerOf(tokenID)
#     # Check balances
#     newBalanceDeployer = token.balanceOf(deployer)
#     newBalanceAlice = token.balanceOf(alice)
#     assert newBalanceDeployer + 1 == oldBalanceDeployer
#     assert oldBalanceAlice + 1 == newBalanceAlice
#     # Verify that an Transfer event has been logged
#     _verifyTransferEvent(txn_receipt, deployer, alice, tokenID)


# #
# # Test ERC165 functions
# #
# def test_ERC615(token):
#     # ERC721
#     assert token.supportsInterface("0x80ac58cd")
#     # ERC165 itself
#     assert token.supportsInterface("0x01ffc9a7")
#     # ERC721 Metadata
#     assert token.supportsInterface("0x5b5e139f")


# #
# # Test name and symbol
# #
# def test_name_symbol(token):
#     name = token.name()
#     symbol = token.symbol()
#     assert len(name) > 0
#     assert len(symbol) > 0


# #
# # Test tokenURI
# #
# def test_token_uri(token, deployer):
#     token_id = 20

#     # Make sure that token does not yet exist
#     _ensureNotToken(token, token_id)

#     # Try to get tokenURI of invalid token - should raise exception
#     with brownie.reverts():  # "ERC721URIStorage: URI query for nonexistent token"):
#         token.tokenURI(token_id)

#     # Mint
#     _ensureToken(token, token_id, deployer)

#     token.set_revealed(True, {"from": token.owner()})

#     # Get base URI
#     base_uri = token.base_uri()

#     # Get token URI
#     token_uri = token.tokenURI(token_id)

#     assert f"{base_uri}{token_id}" == token_uri


# #
# # Test tokenURI - token ID 0
# #
# def test_token_uri_id_zero(token, deployer):
#     token_id = 20
#     # Make sure that token does not yet exist
#     _ensureNotToken(token, token_id)
#     # Try to get tokenURI of invalid token - should raise exception
#     with brownie.reverts():  # "ERC721URIStorage: URI query for nonexistent token"):
#         token.tokenURI(token_id)

#     # Mint
#     _ensureToken(token, token_id, deployer)
#     token.set_revealed(True, {"from": token.owner()})

#     # Get base URI
#     base_uri = token.base_uri()
#     default_uri = token_id

#     # Get token URI
#     token_uri = token.tokenURI(token_id)
#     assert f"{base_uri}{default_uri}" == token_uri