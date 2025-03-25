// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract TemperatureStorage {
    struct TemperatureRecord {
        uint256 temperature;
        uint256 timestamp;
    }

    TemperatureRecord[] public records;
    address public owner;
    uint256 public temperatureThreshold = 3000; // 30.00°C (multiplied by 100)

    event TemperatureLogged(uint256 temperature, uint256 timestamp);
    event MotorStopped(uint256 temperature, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized: Only the owner can log temperature");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function logTemperature(uint256 _temperature) public onlyOwner {
        records.push(TemperatureRecord({
            temperature: _temperature,
            timestamp: block.timestamp
        }));
        emit TemperatureLogged(_temperature, block.timestamp);

        // If temperature >= threshold, trigger motor stop event
        if (_temperature >= temperatureThreshold) {
            emit MotorStopped(_temperature, block.timestamp);
        }
    }

    function getLastTemperature() public view returns (uint256 temperature, uint256 timestamp) {
        require(records.length > 0, "No temperature records available");
        TemperatureRecord memory lastRecord = records[records.length - 1];
        return (lastRecord.temperature, lastRecord.timestamp);
    }

    function updateThreshold(uint256 _newThreshold) public onlyOwner {
        temperatureThreshold = _newThreshold;
    }
}
