# @version 0.3.7

# @notice Frok.AI Vickrey Auction
# @dev Inspired by The Llamas auction house
# @dev This contract does not support rebasing ERC20 tokens, or ERC20 tokens that have a fee on transfer.
# @author johnnyonline
# @license MIT

from vyper.interfaces import ERC20

interface ERC721:
    def mint() -> uint256: nonpayable
    def safeTransferFrom(from_addr: address, to_addr: address, token_id: uint256): nonpayable

interface PriceProvider:
    def get_price(highest_bid: uint256, second_highest_bid: uint256) -> uint256: nonpayable

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

event PriceProviderUpdated:
    price_provider: address

event OwnerUpdated:
    owner: address

event EmergencyPaused:
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
    called_by: indexed(address)
    user: indexed(address)
    reciver: indexed(address)
    amount: uint256


# Technically vyper doesn't need this as it is automatic
# in all recent vyper versions, but Etherscan verification
# will break without it.
IDENTITY_PRECOMPILE: constant(address) = 0x0000000000000000000000000000000000000004

AUCTION_SETTLEMENT_ONLY_OWNER_BUFFER: constant(uint256) = 7200
DURATION_LOWER_BOUND: constant(uint256) = 3600
DURATION_UPPER_BOUND: constant(uint256) = 259200
INCREMENT_PERCENTAGE_LOWER_BOUND: constant(uint256) = 2
INCREMENT_PERCENTAGE_UPPER_BOUND: constant(uint256) = 15
MAX_WITHDRAWALS: constant(uint256) = 100
PRICISION: constant(uint256) = 100

# Auction
time_buffer: public(uint256)
reserve_price: public(uint256)
min_bid_increment_percentage: public(uint256)
duration: public(uint256)

price_provider: public(PriceProvider)
auction: public(Auction)

nft: public(immutable(ERC721))
token: public(immutable(ERC20))

pending_returns: public(HashMap[address, uint256])

# Permissions
owner: public(address)

# Pause
paused: public(bool)
emergency_paused: public(bool)

# Proceeds
proceeds_receiver: public(address)
proceeds_receiver_split_percentage: public(uint256)


### INIT ###


@external
def __init__(
    _nft: ERC721,
    _token: ERC20,
    _price_provider: PriceProvider,
    _time_buffer: uint256,
    _reserve_price: uint256,
    _min_bid_increment_percentage: uint256,
    _duration: uint256,
    _proceeds_receiver_split_percentage: uint256,
    _proceeds_receiver: address,
):
    assert _time_buffer > 0, "_time_buffer must be greater than 0"
    assert _reserve_price > 0, "_reserve_price must be greater than 0"
    assert (
        _min_bid_increment_percentage >= INCREMENT_PERCENTAGE_LOWER_BOUND and
        _min_bid_increment_percentage <= INCREMENT_PERCENTAGE_UPPER_BOUND
    ), "_min_bid_increment_percentage out of range"
    assert _duration >= DURATION_LOWER_BOUND and _duration <= DURATION_UPPER_BOUND, "_duration out of range"
    assert (
        _proceeds_receiver_split_percentage > 0 and _proceeds_receiver_split_percentage < PRICISION
    ), "_proceeds_receiver_split_percentage out of range"
    assert _proceeds_receiver != empty(address), "_proceeds_receiver cannot be empty"

    nft = _nft
    token = _token

    self.price_provider = _price_provider

    self.time_buffer = _time_buffer
    self.reserve_price = _reserve_price
    self.min_bid_increment_percentage = _min_bid_increment_percentage
    self.duration = _duration
    self.proceeds_receiver_split_percentage = _proceeds_receiver_split_percentage
    self.proceeds_receiver = _proceeds_receiver

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
    assert not self.paused, "Auction is paused"

    self._create_auction()


@external
@nonreentrant("lock")
def settle_auction():
    """
    @dev Settle the current auction.
      Throws if the auction is not paused.
    """

    assert self.paused, "Auction is not paused"

    self._settle_auction()


### BIDDING ###


@external
@nonreentrant("lock")
def create_bid(_id: uint256, _bid: uint256):
    """
    @dev Create a bid.
    """

    self._create_bid(_id, _bid)


### WITHDRAW ###


@external
@nonreentrant("lock")
def withdraw(_for: address = msg.sender):
    """
    @dev Withdraw Token after losing auction.
    """

    self._withdraw(_for)


@external
@nonreentrant("lock")
def withdraw_multiple(_fors: DynArray[address, MAX_WITHDRAWALS]):
    """
    @dev Withdraw Token after losing auction, for multiple addresses.
    """

    for _for in _fors:
        self._withdraw(_for)


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
def set_price_provider(_price_provider: address):
    """
    @notice Admin function to set the price provider.
    """

    assert msg.sender == self.owner, "Caller is not the owner"
    assert _price_provider != ZERO_ADDRESS, "Invalid _price_provider address"

    self.price_provider = PriceProvider(_price_provider)

    log PriceProviderUpdated(_price_provider)


@external
def set_owner(_owner: address):
    """
    @notice Admin function to set the owner
    """

    assert msg.sender == self.owner, "Caller is not the owner"
    assert _owner != empty(address), "Cannot set owner to zero address"

    self.owner = _owner

    log OwnerUpdated(_owner)


@external
def emergency_pause():
    """
    @notice Admin function to permanently pause the contract and direct all withdrawals to himself
    """

    assert msg.sender == self.owner, "Caller is not the owner"

    self.emergency_paused = True

    if not self.auction.settled and self.auction.bid > 0:
        self.pending_returns[self.auction.bidder] = self.auction.bid

    log EmergencyPaused(msg.sender)


### INTERNAL FUNCTIONS ###


@internal
def _create_auction():
    assert not self.emergency_paused, "Contract has been emergency paused"

    self.paused = True

    _id: uint256 = nft.mint()
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
    assert not self.emergency_paused, "Contract has been emergency paused"
    assert self.auction.start_time != 0, "Auction hasn't begun"
    assert not self.auction.settled, "Auction has already been settled"
    assert block.timestamp > self.auction.end_time, "Auction hasn't completed"

    if block.timestamp < self.auction.end_time + AUCTION_SETTLEMENT_ONLY_OWNER_BUFFER:
        assert msg.sender == self.owner, "Only owner can settle the auction within 2 hours after it ends"

    self.paused = False
    self.auction.settled = True

    log AuctionSettled(self.auction.nft_id, self.auction.bidder, self.auction.bid, self.auction.price)

    if self.auction.bidder == empty(address):
        nft.safeTransferFrom(self, self.owner, self.auction.nft_id)
    else:
        nft.safeTransferFrom(self, self.auction.bidder, self.auction.nft_id)
        _refund_amount: uint256 = self.auction.bid - self.auction.price
        if _refund_amount > 0:
            self.pending_returns[self.auction.bidder] += _refund_amount

    if self.auction.price > 0:
        _fee: uint256 = (self.auction.price * self.proceeds_receiver_split_percentage) / PRICISION
        _owner_amount: uint256 = self.auction.price - _fee
        token.transfer(self.owner, _owner_amount, default_return_value=True)
        token.transfer(self.proceeds_receiver, _fee, default_return_value=True)


@internal
def _create_bid(_id: uint256, _bid: uint256):
    assert not self.emergency_paused, "Contract has been emergency paused"
    assert self.auction.nft_id == _id, "NFT not up for auction"
    assert block.timestamp < self.auction.end_time, "Auction expired"
    assert _bid >= self.reserve_price, "Must send at least reservePrice"

    _price: uint256 = _bid
    if self.auction.bid > 0:
        assert _bid >= self.auction.bid + (
            (self.auction.bid * self.min_bid_increment_percentage) / PRICISION
        ), "Must send more than last bid by min_bid_increment_percentage amount"

        _price = self.price_provider.get_price(_bid, self.auction.bid)
        assert _bid >= _price, "Bid must be greater than or equal to price"

    _last_bidder: address = self.auction.bidder

    if _last_bidder != empty(address):
        self.pending_returns[_last_bidder] += self.auction.bid

    self.auction.bid = _bid
    self.auction.price = _price
    self.auction.bidder = msg.sender

    _extended: bool = self.auction.end_time - block.timestamp < self.time_buffer

    if _extended:
        self.auction.end_time = block.timestamp + self.time_buffer
        log AuctionExtended(self.auction.nft_id, self.auction.end_time)

    log AuctionBid(self.auction.nft_id, msg.sender, _bid, _price, _extended)

    token.transferFrom(msg.sender, self, _bid, default_return_value=True)


@internal
def _withdraw(_for: address):
    _pending_amount: uint256 = self.pending_returns[_for]
    if _pending_amount > 0:
        self.pending_returns[_for] = 0

        _receiver: address = _for
        if self.emergency_paused: _receiver = self.owner

        log Withdraw(msg.sender, _for, _receiver, _pending_amount)

        token.transfer(_receiver, _pending_amount, default_return_value=True)