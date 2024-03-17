# @version 0.3.7

# @notice Frok.AI Auction Price Provider. Returns the highest bidder's price to pay.
# @dev Price must be lower or equal to the highest bid.
# @author johnnyonline
# @license MIT

event KUpdated:
    k: indexed(uint256)

event OwnerUpdated:
    owner: indexed(address)


k: public(uint256)
owner: public(address)

PRICISION: constant(uint256) = 100


### INIT ###


@external
def __init__(_k: uint256):
    assert _k > 0 and _k < PRICISION, "k out of range"

    self.k = _k
    self.owner = msg.sender


### VIEW FUNCTIONS ###


@external
@view
def get_price(highest_bid: uint256, second_highest_bid: uint256) -> uint256:
    return second_highest_bid + (self.k * (highest_bid - second_highest_bid) / PRICISION)


### ADMIN FUNCTIONS ###


@external
def set_k(_k: uint256):
    assert msg.sender == self.owner, "not owner"
    assert self.k > 0 and self.k < PRICISION, "k out of range"

    self.k = _k

    log KUpdated(_k)

@external
def set_owner(_owner: address):
    assert msg.sender == self.owner, "not owner"
    assert _owner != empty(address), "Cannot set owner to zero address"

    self.owner = _owner

    log OwnerUpdated(_owner)