# @version 0.3.7

# @notice Frok.AI Vickrey Auction
# @dev Inspired by The Llamas auction house
# @author johnnyonline
# @license MIT

interface NFT:
    def mint() -> uint256: nonpayable
    def burn(token_id: uint256): nonpayable
    def transferFrom(from_addr: address, to_addr: address, token_id: uint256): nonpayable

struct Auction:
        nft_id: uint256
        bid: uint256
        price: uint256
        start_time: uint256
        end_time: uint256
        bidder: address
        settled: bool

event AuctionBid:
    nft_id: indexed(uint256)
    sender: address
    bid: uint256
    price: uint256
    extended: bool

event AuctionExtended:
    nft_id: indexed(uint256)
    end_time: uint256

event AuctionTimeBufferUpdated:
    time_buffer: uint256

event AuctionReservePriceUpdated:
    reserve_price: uint256

event AuctionMinBidIncrementPercentageUpdated:
    min_bid_increment_percentage: uint256

event AuctionDurationUpdated:
    duration: uint256

event KUpdated:
    k: uint256

event OwnerUpdated:
    owner: address

event AuctionCreated:
    nft_id: indexed(uint256)
    start_time: uint256
    end_time: uint256

event AuctionSettled:
    nft_id: indexed(uint256)
    winner: address
    bid: uint256
    price: uint256

event Withdraw:
    _withdrawer: indexed(address)
    _amount: uint256


# Technically vyper doesn't need this as it is automatic
# in all recent vyper versions, but Etherscan verification
# will break without it.
IDENTITY_PRECOMPILE: constant(address) = 0x0000000000000000000000000000000000000004

PRICISION: constant(uint256) = 100
INCREMENT_PERCENTAGE_LOWER_BOUND: constant(uint256) = 2
INCREMENT_PERCENTAGE_UPPER_BOUND: constant(uint256) = 15
DURATION_LOWER_BOUND: constant(uint256) = 3600
DURATION_UPPER_BOUND: constant(uint256) = 259200

# Auction
time_buffer: public(uint256)
reserve_price: public(uint256)
min_bid_increment_percentage: public(uint256)
duration: public(uint256)
k: public(uint256)
nft: public(NFT)
auction: public(Auction)
pending_returns: public(HashMap[address, uint256])

# Permissions
owner: public(address)

# Pause
paused: public(bool)

# Proceeds
proceeds_receiver: public(address)
proceeds_receiver_split_percentage: public(uint256)


### INIT ###


@external
def __init__(
    _nft: NFT,
    _time_buffer: uint256,
    _reserve_price: uint256,
    _min_bid_increment_percentage: uint256,
    _duration: uint256,
    _proceeds_receiver: address,
    _proceeds_receiver_split_percentage: uint256,
    _k: uint256
):
    assert _time_buffer > 0, "_time_buffer must be greater than 0"
    assert _reserve_price > 0, "_reserve_price must be greater than 0"
    assert (
        _min_bid_increment_percentage >= INCREMENT_PERCENTAGE_LOWER_BOUND and
        _min_bid_increment_percentage <= INCREMENT_PERCENTAGE_UPPER_BOUND
    ), "_min_bid_increment_percentage out of range"
    assert _duration >= DURATION_LOWER_BOUND and _duration <= DURATION_UPPER_BOUND, "_duration out of range"
    assert _proceeds_receiver != empty(address), "_proceeds_receiver cannot be empty"
    assert (
        _proceeds_receiver_split_percentage > 0 and _proceeds_receiver_split_percentage < PRICISION
    ), "_proceeds_receiver_split_percentage out of range"
    assert _k > 0 and _k < PRICISION, "k out of range"

    self.nft = _nft
    self.time_buffer = _time_buffer
    self.reserve_price = _reserve_price
    self.min_bid_increment_percentage = _min_bid_increment_percentage
    self.duration = _duration
    self.proceeds_receiver = _proceeds_receiver
    self.proceeds_receiver_split_percentage = _proceeds_receiver_split_percentage
    self.k = _k

    self.owner = msg.sender


### AUCTION CREATION/SETTLEMENT ###


@external
@nonreentrant("lock")
def create_auction():
    """
    @dev Create a new auction.
      Throws if the auction is paused.
      Only Admin can call this function.
    """

    assert msg.sender == self.owner, "Caller is not the owner"
    assert self.paused == False, "Auction is paused"

    self._create_auction()

@external
@nonreentrant("lock")
def settle_auction():
    """
    @dev Settle the current auction.
      Throws if the auction is not paused.
    """

    assert self.paused == True, "Auction is not paused"

    self._settle_auction()


### BIDDING ###


@external
@payable
@nonreentrant("lock")
def create_bid(_id: uint256, _bid_amount: uint256):
    """
    @dev Create a bid.
    """

    self._create_bid(_id, _bid_amount)


### WITHDRAW ###


@external
@nonreentrant("lock")
def withdraw():
    """
    @dev Withdraw ETH after losing auction.
    """

    _pending_amount: uint256 = self.pending_returns[msg.sender]
    self.pending_returns[msg.sender] = 0
    raw_call(msg.sender, b"", value=_pending_amount)

    log Withdraw(msg.sender, _pending_amount)


### ADMIN FUNCTIONS ###


@external
def set_time_buffer(_time_buffer: uint256):
    """
    @notice Admin function to set the time buffer.
    """

    assert msg.sender == self.owner, "Caller is not the owner"

    self.time_buffer = _time_buffer

    log AuctionTimeBufferUpdated(_time_buffer)

@external
def set_reserve_price(_reserve_price: uint256):
    """
    @notice Admin function to set the reserve price.
    """

    assert msg.sender == self.owner, "Caller is not the owner"

    self.reserve_price = _reserve_price

    log AuctionReservePriceUpdated(_reserve_price)

@external
def set_min_bid_increment_percentage(_min_bid_increment_percentage: uint256):
    """
    @notice Admin function to set the min bid increment percentage.
    """

    assert msg.sender == self.owner, "Caller is not the owner"
    assert (
        _min_bid_increment_percentage >= INCREMENT_PERCENTAGE_LOWER_BOUND and
        _min_bid_increment_percentage <= INCREMENT_PERCENTAGE_UPPER_BOUND
    ), "_min_bid_increment_percentage out of range"

    self.min_bid_increment_percentage = _min_bid_increment_percentage

    log AuctionMinBidIncrementPercentageUpdated(_min_bid_increment_percentage)

@external
def set_duration(_duration: uint256):
    """
    @notice Admin function to set the duration.
    """

    assert msg.sender == self.owner, "Caller is not the owner"
    assert _duration >= DURATION_LOWER_BOUND and _duration <= DURATION_UPPER_BOUND, "_duration out of range"

    self.duration = _duration

    log AuctionDurationUpdated(_duration)

@external
def set_k(_k: uint256):
    """
    @notice Admin function to set the k value.
    """

    assert msg.sender == self.owner, "Caller is not the owner"
    assert _k > 0 and _k < PRICISION, "k out of range"

    self.k = _k

    log KUpdated(_k)

@external
def set_owner(_owner: address):
    """
    @notice Admin function to set the owner
    """

    assert msg.sender == self.owner, "Caller is not the owner"
    assert _owner != empty(address), "Cannot set owner to zero address"

    self.owner = _owner

    log OwnerUpdated(_owner)


### INTERNAL FUNCTIONS ###


@internal
def _create_auction():

    self.paused = True

    _id: uint256 = self.nft.mint()
    _start_time: uint256 = block.timestamp
    _end_time: uint256 = _start_time + self.duration

    self.auction = Auction(
        {
            nft_id: _id,
            bid: 0,
            price: 0,
            start_time: _start_time,
            end_time: _end_time,
            bidder: empty(address),
            settled: False,
        }
    )

    log AuctionCreated(_id, _start_time, _end_time)

@internal
def _settle_auction():
    assert self.auction.start_time != 0, "Auction hasn't begun"
    assert self.auction.settled == False, "Auction has already been settled"
    assert block.timestamp > self.auction.end_time, "Auction hasn't completed"

    self.paused = False
    self.auction.settled = True

    if self.auction.bidder == empty(address):
        self.nft.transferFrom(self, self.owner, self.auction.nft_id)
    else:
        self.nft.transferFrom(self, self.auction.bidder, self.auction.nft_id)

    if self.auction.price > 0:
        fee: uint256 = (self.auction.price * self.proceeds_receiver_split_percentage) / PRICISION
        owner_amount: uint256 = self.auction.price - fee
        raw_call(self.owner, b"", value=owner_amount)
        raw_call(self.proceeds_receiver, b"", value=fee)

    log AuctionSettled(self.auction.nft_id, self.auction.bidder, self.auction.bid, self.auction.price)

@internal
@payable
def _create_bid(_id: uint256, _bid: uint256):
    assert self.auction.nft_id == _id, "NFT not up for auction"
    assert block.timestamp < self.auction.end_time, "Auction expired"
    assert _bid >= self.reserve_price, "Must send at least reservePrice"

    _price: uint256 = _bid
    if self.auction.bid > 0:
        assert _bid >= self.auction.bid + (
            (self.auction.bid * self.min_bid_increment_percentage) / PRICISION
        ), "Must send more than last bid by min_bid_increment_percentage amount"

        _price = self.auction.bid + (self.k * (_bid - self.auction.bid) / PRICISION) # @todo - get from external contract

    assert msg.value == _price, "Sent value does not equal price" # @todo - enable ERC20

    _last_bidder: address = self.auction.bidder

    if _last_bidder != empty(address):
        self.pending_returns[_last_bidder] += self.auction.price

    self.auction.bid = _bid
    self.auction.price = _price
    self.auction.bidder = msg.sender

    _extended: bool = self.auction.end_time - block.timestamp < self.time_buffer

    if _extended:
        self.auction.end_time = block.timestamp + self.time_buffer
        log AuctionExtended(self.auction.nft_id, self.auction.end_time)

    log AuctionBid(self.auction.nft_id, msg.sender, _bid, _price, _extended)