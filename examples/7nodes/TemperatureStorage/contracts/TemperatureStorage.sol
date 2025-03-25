// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract TemperatureStorage {
    struct TemperatureRecord {
        uint256 temperature;
        uint256 timestamp;
    }

    TemperatureRecord[] public records;
    address public owner;

    event TemperatureLogged(uint256 temperature, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized: Only the owner can log temperature");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function logTemperature(uint256 _temperature) public onlyOwner {
        require(_temperature > 30, "Temperature must be greater than 30 degrees Celsius");
        records.push(TemperatureRecord({
            temperature: _temperature,
            timestamp: block.timestamp
        }));
        emit TemperatureLogged(_temperature, block.timestamp);
    }

    function getLastTemperature() public view returns (uint256 temperature, uint256 timestamp) {
        require(records.length > 0, "No temperature records available");
        TemperatureRecord memory lastRecord = records[records.length - 1];
        return (lastRecord.temperature, lastRecord.timestamp);
    }
}