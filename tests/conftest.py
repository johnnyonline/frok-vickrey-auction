import pytest

@pytest.fixture(scope="function")
def token(project, deployer):
    return deployer.deploy(project.Frok)


@pytest.fixture(scope="function")
def token_minted(token, deployer):
    token.mint(deployer)
    return token


@pytest.fixture(scope="function")
def deployer(accounts):
    return accounts[0]


@pytest.fixture(scope="function")
def split_recipient(accounts):
    return accounts[1]


@pytest.fixture(scope="function")
def smart_contract_owner(BasicSafe, deployer):
    return deployer.BasicSafe.deploy()


@pytest.fixture(scope="function")
def alice(accounts):
    return accounts[2]


@pytest.fixture(scope="function")
def bob(accounts):
    return accounts[3]


@pytest.fixture(scope="function")
def charlie(accounts):
    return accounts[4]


@pytest.fixture(scope="function")
def minted(token, deployer):
    token.mint(sender=deployer)
    return token


@pytest.fixture(scope="function")
def minted_token_id():
    return 0


# @pytest.fixture(scope="function")
# def token_metadata():
#     return {"name": "Frok", "symbol": "FROK"}


# @pytest.fixture(scope="function")
# def tokenReceiver(deployer):
#     return ERC721TokenReceiverImplementation.deploy({"from": deployer})


# @pytest.fixture(scope="function")
# def erc20token(deployer, BasicERC20):
#     return BasicERC20.deploy({"from": deployer})


# @pytest.fixture(scope="function")
# def minted_erc20token_to_users(erc20token, alice, bob, charlie):
#     erc20token.mint(alice, 1000 * 10 ** 18, {"from": deployer})
#     erc20token.mint(bob, 1000 * 10 ** 18, {"from": deployer})
#     erc20token.mint(charlie, 1000 * 10 ** 18, {"from": deployer})


# @pytest.fixture(scope="function")
# def price_provider(deployer, PriceProvider):
#     return PriceProvider.deploy(0.5, {"from": deployer})


# @pytest.fixture(scope="function") # @todo
# def auction_house(VickreyAuction, token, erc20token, price_provider, deployer, split_recipient):
#     auction_house = VickreyAuction.deploy(
#         token, erc20token, price_provider, 100, 100, 5, 3600, 95, split_recipient.address, {"from": deployer}
#     )
#     return auction_house


# @pytest.fixture(scope="function")
# def auction_house_unpaused(VickreyAuction, token, deployer, split_recipient):
#     auction_house = VickreyAuction.deploy(
#         token, 100, 100, 5, 100, split_recipient.address, 95, {"from": deployer}
#     )
#     token.set_minter(auction_house)
#     auction_house.unpause()
#     return auction_house


# @pytest.fixture(scope="function")
# def auction_house_sc_owner(
#     VickreyAuction, token, deployer, smart_contract_owner, split_recipient
# ):
#     auction_house = VickreyAuction.deploy(
#         token, 100, 100, 5, 100, split_recipient.address, 95, {"from": deployer}
#     )
#     token.set_minter(auction_house)
#     auction_house.unpause()
#     auction_house.disable_wl()
#     auction_house.set_owner(smart_contract_owner, {"from": deployer})
#     return auction_house