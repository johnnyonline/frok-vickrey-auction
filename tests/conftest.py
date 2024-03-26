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


@pytest.fixture(scope="function")
def erc20token(project, deployer):
    return project.BasicERC20.deploy(sender=deployer)


@pytest.fixture(scope="function")
def minted_erc20token_to_users(erc20token, alice, bob, charlie, deployer):
    erc20token.mint(alice, 1000 * 10 ** 18, sender=deployer)
    erc20token.mint(bob, 1000 * 10 ** 18, sender=deployer)
    erc20token.mint(charlie, 1000 * 10 ** 18, sender=deployer)
    return erc20token


@pytest.fixture(scope="function")
def price_provider(project, deployer):
    return project.PriceProvider.deploy(50, sender=deployer)


@pytest.fixture(scope="function")
def vickrey_auction(project, token, erc20token, price_provider, deployer, split_recipient):
    vickrey_auction = project.VickreyAuction.deploy(
        token,
        erc20token,
        price_provider, 
        100, # time_buffer
        100, # reserve_price
        5, # min_bid_increment_percentage
        3600, # duration
        95, # _proceeds_receiver_split_percentage
        split_recipient,
        sender=deployer
    )
    return vickrey_auction


@pytest.fixture(scope="function")
def vickrey_auction_created(vickrey_auction, token, deployer):
    token.set_minter(vickrey_auction, sender=deployer)
    vickrey_auction.create_auction(sender=deployer)
    return vickrey_auction