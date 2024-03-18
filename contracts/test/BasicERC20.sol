// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import {ERC20} from "@openzeppelin/token/ERC20/ERC20.sol";

contract BasicERC20 is ERC20 {

    address public owner;

    constructor() ERC20("BasicERC20", "B20") {
        owner = msg.sender;
    }

    function mint(address to, uint256 amount) external {
        require(msg.sender == owner, "BasicERC20: only owner can mint");
        _mint(to, amount);
    }
}