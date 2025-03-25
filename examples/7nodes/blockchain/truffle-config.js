module.exports = {
  networks: {
    quorum: {
      host: "127.0.0.1",
      port: 22000,
      network_id: "*",
      gas: 8000000,
      gasPrice: 0,
    }
  },
  compilers: {
    solc: {
      version: "0.8.17"
    }
  }
};