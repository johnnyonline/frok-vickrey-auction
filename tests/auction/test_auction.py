import ape


# Helper methods


def create_pending_returns(vickrey_auction_created, bidder_1, bidder_2, minted_erc20token_to_users):
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=bidder_1)
    vickrey_auction_created.create_bid(0, 100, sender=bidder_1)
    minted_erc20token_to_users.approve(vickrey_auction_created, 200, sender=bidder_2)
    vickrey_auction_created.create_bid(0, 200, sender=bidder_2)


# Initialization vars


def test_owner(vickrey_auction, deployer):
    assert vickrey_auction.owner() == deployer


def test_token(vickrey_auction, token):
    assert vickrey_auction.nft() == token


def test_time_buffer(vickrey_auction):
    assert vickrey_auction.time_buffer() == 100


def test_bid_after(vickrey_auction):
    assert vickrey_auction.reserve_price() == 100


def test_min_bid_increment_percentage(vickrey_auction):
    assert vickrey_auction.min_bid_increment_percentage() == 5


def test_duration(vickrey_auction):
    assert vickrey_auction.duration() == 3600


def test_paused(vickrey_auction):
    assert not vickrey_auction.paused()


def test_price_provider(vickrey_auction, price_provider):
    assert vickrey_auction.price_provider() == price_provider


def test_emergency_pause(vickrey_auction):
    assert not vickrey_auction.emergency_paused()


# Owner control


def test_set_owner(vickrey_auction, deployer, alice):
    vickrey_auction.set_owner(alice, sender=deployer)
    assert vickrey_auction.owner() == alice


def test_set_owner_zero_address(vickrey_auction, deployer):
    with ape.reverts("Cannot set owner to zero address"):
        vickrey_auction.set_owner(ape.utils.ZERO_ADDRESS, sender=deployer)
    assert vickrey_auction.owner() == deployer


def test_set_time_buffer(vickrey_auction, deployer):
    vickrey_auction.set_time_buffer(200, sender=deployer)
    assert vickrey_auction.time_buffer() == 200


def test_set_reserve_price(vickrey_auction, deployer):
    vickrey_auction.set_reserve_price(200, sender=deployer)
    assert vickrey_auction.reserve_price() == 200


def test_set_min_bid_increment_percentage(vickrey_auction, deployer):
    vickrey_auction.set_min_bid_increment_percentage(15, sender=deployer)
    assert vickrey_auction.min_bid_increment_percentage() == 15


def test_set_min_bid_increment_percentage_above_range(vickrey_auction, deployer):
    with ape.reverts("_min_bid_increment_percentage out of range"):
        vickrey_auction.set_min_bid_increment_percentage(16, sender=deployer)
    assert vickrey_auction.min_bid_increment_percentage() == 5


def test_set_min_bid_increment_percentage_below_range(vickrey_auction, deployer):
    with ape.reverts("_min_bid_increment_percentage out of range"):
        vickrey_auction.set_min_bid_increment_percentage(1, sender=deployer)
    assert vickrey_auction.min_bid_increment_percentage() == 5


def test_set_duration(vickrey_auction, deployer):
    vickrey_auction.set_duration(4000, sender=deployer)
    assert vickrey_auction.duration() == 4000


def test_set_duration_above_range(vickrey_auction, deployer):
    with ape.reverts("_duration out of range"):
        vickrey_auction.set_duration(260000, sender=deployer)
    assert vickrey_auction.duration() == 3600


def test_set_duration_below_range(vickrey_auction, deployer):
    with ape.reverts("_duration out of range"):
        vickrey_auction.set_duration(3599, sender=deployer)
    assert vickrey_auction.duration() == 3600


def test_set_price_provider_zero_address(vickrey_auction, deployer):
    with ape.reverts("Invalid _price_provider address"):
        vickrey_auction.set_price_provider(ape.utils.ZERO_ADDRESS, sender=deployer)


def test_emergency_paused(vickrey_auction, deployer):
    assert not vickrey_auction.emergency_paused()
    vickrey_auction.emergency_pause(sender=deployer)
    assert vickrey_auction.emergency_paused()


def test_emergency_paused_not_owner(vickrey_auction, alice):
    with ape.reverts("Caller is not the owner"):
        vickrey_auction.emergency_pause(sender=alice)


def test_set_price_provider_not_owner(vickrey_auction, alice):
    with ape.reverts("Caller is not the owner"):
        vickrey_auction.set_price_provider(ape.utils.ZERO_ADDRESS, sender=alice)


def test_emergency_pause_not_owner(vickrey_auction, alice):
    with ape.reverts("Caller is not the owner"):
        vickrey_auction.emergency_pause(sender=alice)


def test_set_owner_not_owner(vickrey_auction, alice):
    with ape.reverts("Caller is not the owner"):
        vickrey_auction.set_owner(alice, sender=alice)


def test_set_time_buffer_not_owner(vickrey_auction, alice):
    with ape.reverts("Caller is not the owner"):
        vickrey_auction.set_time_buffer(200, sender=alice)


def test_set_reserve_price_not_owner(vickrey_auction, alice):
    with ape.reverts("Caller is not the owner"):
        vickrey_auction.set_reserve_price(200, sender=alice)


def test_set_min_bid_increment_percentage_not_owner(vickrey_auction, alice):
    with ape.reverts("Caller is not the owner"):
        vickrey_auction.set_min_bid_increment_percentage(200, sender=alice)


def test_set_duration_not_owner(vickrey_auction, alice):
    with ape.reverts("Caller is not the owner"):
        vickrey_auction.set_duration(1000, sender=alice)


# Public Bidding
        
# @todo (1) test_create_bid_send_eth - fail


def test_create_bid(vickrey_auction_created, alice, minted_erc20token_to_users):
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    vickrey_auction_created.create_bid(0, 100, sender=alice)
    current_auction = vickrey_auction_created.auction()
    assert current_auction["bidder"] == alice
    assert current_auction["bid"] == 100
    assert current_auction["price"] == 100
    assert current_auction["end_time"] == current_auction["start_time"] + vickrey_auction_created.duration()


def test_create_bid_send_more_than_last_bid(vickrey_auction_created, alice, bob, minted_erc20token_to_users, price_provider):
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    vickrey_auction_created.create_bid(0, 100, sender=alice)
    current_auction = vickrey_auction_created.auction()
    assert current_auction["bidder"] == alice
    assert current_auction["bid"] == 100
    assert current_auction["price"] == 100
    assert current_auction["end_time"] == current_auction["start_time"] + vickrey_auction_created.duration()

    minted_erc20token_to_users.approve(vickrey_auction_created, 1000, sender=bob)
    vickrey_auction_created.create_bid(0, 1000, sender=bob)
    current_auction = vickrey_auction_created.auction()
    assert current_auction["bidder"] == bob
    assert current_auction["bid"] == 1000
    assert current_auction["price"] == price_provider.get_price(1000, 100, sender=bob)
    assert current_auction["end_time"] == current_auction["start_time"] + vickrey_auction_created.duration()


def test_create_bid_wrong_nft_id(vickrey_auction_created, alice, minted_erc20token_to_users):
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    with ape.reverts("NFT not up for auction"):
        vickrey_auction_created.create_bid(1, 100, sender=alice)


def test_create_bid_auction_expired(chain, vickrey_auction_created, alice, minted_erc20token_to_users):
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    # Expire the auction
    chain.pending_timestamp += 4000
    with ape.reverts("Auction expired"):
        vickrey_auction_created.create_bid(0, 100, sender=alice)


def test_create_bid_value_too_low(vickrey_auction_created, alice, minted_erc20token_to_users):
    minted_erc20token_to_users.approve(vickrey_auction_created, 1, sender=alice)
    with ape.reverts("Must send at least reservePrice"):
        vickrey_auction_created.create_bid(0, 1, sender=alice)


def test_create_bid_not_over_prev_bid(vickrey_auction_created, alice, bob, minted_erc20token_to_users):
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    vickrey_auction_created.create_bid(0, 100, sender=alice)
    current_auction = vickrey_auction_created.auction()
    assert current_auction["bidder"] == alice
    assert current_auction["bid"] == 100
    assert current_auction["price"] == 100
    assert current_auction["end_time"] == current_auction["start_time"] + vickrey_auction_created.duration()

    minted_erc20token_to_users.approve(vickrey_auction_created, 101, sender=bob)
    with ape.reverts("Must send more than last bid by min_bid_increment_percentage amount"):
        vickrey_auction_created.create_bid(0, 101, sender=bob)

    bid_after = vickrey_auction_created.auction()
    assert bid_after["bidder"] == alice
    assert bid_after["bid"] == 100
    assert bid_after["price"] == 100
    assert bid_after["end_time"] == bid_after["start_time"] + vickrey_auction_created.duration()


# WITHDRAW


def test_create_second_bid_and_withdraw(vickrey_auction_created, alice, bob, minted_erc20token_to_users, price_provider):
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    vickrey_auction_created.create_bid(0, 100, sender=alice)
    bid_before = vickrey_auction_created.auction()
    assert bid_before["bidder"] == alice
    assert bid_before["bid"] == 100
    assert bid_before["price"] == 100
    assert bid_before["end_time"] == bid_before["start_time"] + vickrey_auction_created.duration()
    alice_balance_before = minted_erc20token_to_users.balanceOf(alice, sender=alice)

    minted_erc20token_to_users.approve(vickrey_auction_created, 1000, sender=bob)
    vickrey_auction_created.create_bid(0, 1000, sender=bob)

    bid_after = vickrey_auction_created.auction()
    assert bid_after["bidder"] == bob
    assert bid_after["bid"] == 1000
    assert bid_after["price"] == price_provider.get_price(1000, 100, sender=bob)
    assert bid_after["end_time"] == bid_after["start_time"] + vickrey_auction_created.duration()

    vickrey_auction_created.withdraw(sender=alice)

    alice_balance_after = minted_erc20token_to_users.balanceOf(alice, sender=alice)

    assert alice_balance_after == alice_balance_before + 100


def test_withdraw_zero_pending(vickrey_auction_created, alice, minted_erc20token_to_users):
    balance_before = minted_erc20token_to_users.balanceOf(alice, sender=alice)
    vickrey_auction_created.withdraw(sender=alice)
    balance_after = minted_erc20token_to_users.balanceOf(alice, sender=alice)
    assert balance_before == balance_after


def test_emergency_withdraw(vickrey_auction_created, deployer, alice, bob, minted_erc20token_to_users):
    balance_of_alice_before = minted_erc20token_to_users.balanceOf(alice, sender=alice)
    balance_of_bob_before = minted_erc20token_to_users.balanceOf(bob, sender=bob)
    balance_of_deployer_before = minted_erc20token_to_users.balanceOf(deployer, sender=deployer)

    create_pending_returns(vickrey_auction_created, alice, bob, minted_erc20token_to_users)

    vickrey_auction_created.emergency_pause(sender=deployer)

    assert minted_erc20token_to_users.balanceOf(deployer, sender=deployer) == balance_of_deployer_before
    assert minted_erc20token_to_users.balanceOf(alice, sender=alice) == balance_of_alice_before - 100
    assert minted_erc20token_to_users.balanceOf(bob, sender=bob) == balance_of_bob_before - 200
    assert vickrey_auction_created.pending_returns(alice) == 100
    assert vickrey_auction_created.pending_returns(bob) == 200

    vickrey_auction_created.withdraw_multiple([alice.address, bob.address], sender=alice)

    assert vickrey_auction_created.pending_returns(alice) == 0
    assert vickrey_auction_created.pending_returns(bob) == 0
    assert minted_erc20token_to_users.balanceOf(alice, sender=alice) == balance_of_alice_before - 100
    assert minted_erc20token_to_users.balanceOf(bob, sender=bob) == balance_of_bob_before - 200
    assert (minted_erc20token_to_users.balanceOf(deployer, sender=deployer) == balance_of_deployer_before + 300)


def test_settle_auction_no_bid(chain, vickrey_auction_created, token, alice, deployer):
    assert not vickrey_auction_created.auction()["settled"]

    chain.pending_timestamp += vickrey_auction_created.duration()

    with ape.reverts("Only owner can settle the auction within 2 hours after it ends"):
        vickrey_auction_created.settle_auction(sender=alice)
    
    chain.pending_timestamp += 7200 # vickrey_auction_created.AUCTION_SETTLEMENT_ONLY_OWNER_BUFFER()

    vickrey_auction_created.settle_auction(sender=alice)

    assert vickrey_auction_created.auction()["settled"]
    # Token was transferred to owner when no one bid
    assert token.ownerOf(0) == deployer


def test_settle_auction_when_not_paused(vickrey_auction, deployer):
    with ape.reverts("Auction is not paused"):
        vickrey_auction.settle_auction(sender=deployer)


def test_settle_current_and_create_new_auction_no_bid(chain, token, deployer, vickrey_auction_created, split_recipient):
    assert not vickrey_auction_created.auction()["settled"]
    old_auction_id = vickrey_auction_created.auction()["nft_id"]
    chain.pending_timestamp += vickrey_auction_created.duration()
    vickrey_auction_created.settle_auction(sender=deployer)
    vickrey_auction_created.create_auction(sender=deployer)
    new_auction_id = vickrey_auction_created.auction()["nft_id"]
    assert not vickrey_auction_created.auction()["settled"]
    assert old_auction_id < new_auction_id
    # Token was transferred to owner when no one bid
    assert token.ownerOf(0) == deployer


def test_settle_auction_with_bid(chain, token, deployer, vickrey_auction_created, alice, split_recipient, minted_erc20token_to_users):
    assert not vickrey_auction_created.auction()["settled"]
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    vickrey_auction_created.create_bid(0, 100, sender=alice)
    chain.pending_timestamp += vickrey_auction_created.duration()
    deployer_balance_before = minted_erc20token_to_users.balanceOf(deployer, sender=deployer)
    split_recipient_before = minted_erc20token_to_users.balanceOf(split_recipient, sender=split_recipient)
    vickrey_auction_created.settle_auction(sender=deployer)
    deployer_balance_after = minted_erc20token_to_users.balanceOf(deployer, sender=deployer)
    split_recipient_after = minted_erc20token_to_users.balanceOf(split_recipient, sender=split_recipient)
    assert vickrey_auction_created.auction()["settled"]
    assert token.ownerOf(0) == alice
    assert deployer_balance_after == deployer_balance_before + 5
    assert split_recipient_after == split_recipient_before + 95


def test_settle_current_and_create_new_auction_with_bid(
        chain, deployer, vickrey_auction_created, alice, split_recipient, minted_erc20token_to_users
    ):
    assert not vickrey_auction_created.auction()["settled"]
    old_auction_id = vickrey_auction_created.auction()["nft_id"]
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    vickrey_auction_created.create_bid(0, 100, sender=alice)
    chain.pending_timestamp += vickrey_auction_created.duration()
    deployer_balance_before = minted_erc20token_to_users.balanceOf(deployer, sender=deployer)
    split_recipient_before = minted_erc20token_to_users.balanceOf(split_recipient, sender=split_recipient)
    vickrey_auction_created.settle_auction(sender=deployer)
    vickrey_auction_created.create_auction(sender=deployer)
    deployer_balance_after = minted_erc20token_to_users.balanceOf(deployer, sender=deployer)
    split_recipient_after = minted_erc20token_to_users.balanceOf(split_recipient, sender=split_recipient)
    new_auction_id = vickrey_auction_created.auction()["nft_id"]
    assert not vickrey_auction_created.auction()["settled"]
    assert old_auction_id < new_auction_id
    assert deployer_balance_after == deployer_balance_before + 5
    assert split_recipient_after == split_recipient_before + 95


def test_settle_auction_multiple_bids(
    chain, token, deployer, vickrey_auction_created, split_recipient, alice, bob, minted_erc20token_to_users
):
    assert not vickrey_auction_created.auction()["settled"]
    alice_balance_start = minted_erc20token_to_users.balanceOf(alice, sender=alice)
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    vickrey_auction_created.create_bid(0, 100, sender=alice)
    minted_erc20token_to_users.approve(vickrey_auction_created, 1000, sender=bob)
    vickrey_auction_created.create_bid(0, 1000, sender=bob)
    chain.pending_timestamp += vickrey_auction_created.duration()
    deployer_balance_before = minted_erc20token_to_users.balanceOf(deployer, sender=deployer)
    split_recipient_before = minted_erc20token_to_users.balanceOf(split_recipient, sender=split_recipient)
    vickrey_auction_created.settle_auction(sender=deployer)
    deployer_balance_after = minted_erc20token_to_users.balanceOf(deployer, sender=deployer)
    split_recipient_after = minted_erc20token_to_users.balanceOf(split_recipient, sender=split_recipient)
    alice_balance_before_withdraw = minted_erc20token_to_users.balanceOf(alice, sender=alice)
    assert alice_balance_before_withdraw == alice_balance_start - 100
    vickrey_auction_created.withdraw(sender=alice)
    alice_balance_after_withdraw = minted_erc20token_to_users.balanceOf(alice, sender=alice)
    assert alice_balance_after_withdraw == alice_balance_start
    assert vickrey_auction_created.auction()["settled"]
    assert token.ownerOf(0) == bob
    assert deployer_balance_after == deployer_balance_before + 28
    assert split_recipient_after == split_recipient_before + 522


def test_bidder_outbids_prev_bidder(
    chain, token, vickrey_auction_created, deployer, split_recipient, alice, bob, minted_erc20token_to_users
):
    assert not vickrey_auction_created.auction()["settled"]
    alice_balance_start = minted_erc20token_to_users.balanceOf(alice, sender=alice)
    bob_balance_start = minted_erc20token_to_users.balanceOf(bob, sender=bob)
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    vickrey_auction_created.create_bid(0, 100, sender=alice)
    minted_erc20token_to_users.approve(vickrey_auction_created, 1000, sender=bob)
    vickrey_auction_created.create_bid(0, 1000, sender=bob)
    minted_erc20token_to_users.approve(vickrey_auction_created, 2000, sender=alice)
    vickrey_auction_created.create_bid(0, 2000, sender=alice)
    chain.pending_timestamp += vickrey_auction_created.duration()
    deployer_balance_before = minted_erc20token_to_users.balanceOf(deployer, sender=deployer)
    split_recipient_before = minted_erc20token_to_users.balanceOf(split_recipient, sender=split_recipient)
    price = vickrey_auction_created.auction()["price"]
    vickrey_auction_created.settle_auction(sender=deployer)
    vickrey_auction_created.create_auction(sender=deployer)
    deployer_balance_after = minted_erc20token_to_users.balanceOf(deployer, sender=deployer)
    split_recipient_after = minted_erc20token_to_users.balanceOf(split_recipient, sender=split_recipient)
    alice_balance_before_withdraw = minted_erc20token_to_users.balanceOf(alice, sender=alice)
    bob_balance_before_withdraw = minted_erc20token_to_users.balanceOf(bob, sender=bob)
    assert alice_balance_before_withdraw == alice_balance_start - 2100
    assert bob_balance_before_withdraw == bob_balance_start - 1000
    vickrey_auction_created.withdraw(sender=alice)
    vickrey_auction_created.withdraw(sender=bob)
    alice_balance_after_withdraw = minted_erc20token_to_users.balanceOf(alice, sender=alice)
    bob_balance_after_withdraw = minted_erc20token_to_users.balanceOf(bob, sender=bob)
    assert alice_balance_after_withdraw == alice_balance_start - price
    assert bob_balance_after_withdraw == bob_balance_start
    assert not vickrey_auction_created.auction()["settled"]
    assert token.ownerOf(0) == alice
    assert deployer_balance_after == deployer_balance_before + (price * 5 / 100)
    assert split_recipient_after == split_recipient_before + (price * 95 / 100)


# AUCTION EXTENSION


def test_create_bid_auction_extended(chain, vickrey_auction_created, alice, bob, minted_erc20token_to_users):
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    vickrey_auction_created.create_bid(0, 100, sender=alice)
    starting_block_timestamp = chain.pending_timestamp
    chain.pending_timestamp += 3550
    minted_erc20token_to_users.approve(vickrey_auction_created, 1000, sender=bob)
    vickrey_auction_created.create_bid(0, 1000, sender=bob)
    assert vickrey_auction_created.auction()["end_time"] == chain.pending_timestamp + vickrey_auction_created.time_buffer() - 1
    assert not vickrey_auction_created.auction()["settled"]


def test_create_bid_auction_not_extended(chain, vickrey_auction_created, alice, bob, minted_erc20token_to_users):
    minted_erc20token_to_users.approve(vickrey_auction_created, 100, sender=alice)
    vickrey_auction_created.create_bid(0, 100, sender=alice)
    chain.pending_timestamp += vickrey_auction_created.duration() + 1
    minted_erc20token_to_users.approve(vickrey_auction_created, 1000, sender=bob)
    with ape.reverts("Auction expired"):
        vickrey_auction_created.create_bid(0, 1000, sender=bob)