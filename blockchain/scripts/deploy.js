const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);

  // Deploy AgriDAO
  const AgriDAO = await hre.ethers.getContractFactory("AgriDAO");
  const agriDAO = await AgriDAO.deploy();
  await agriDAO.waitForDeployment();
  const agriDAOAddress = await agriDAO.getAddress();
  console.log("AgriDAO deployed to:", agriDAOAddress);

  // Deploy MarketplaceEscrow
  const MarketplaceEscrow = await hre.ethers.getContractFactory("MarketplaceEscrow");
  const escrow = await MarketplaceEscrow.deploy(deployer.address);
  await escrow.waitForDeployment();
  const escrowAddress = await escrow.getAddress();
  console.log("MarketplaceEscrow deployed to:", escrowAddress);

  // Save addresses
  const addresses = {
    agriDAO: agriDAOAddress,
    marketplaceEscrow: escrowAddress,
    network: hre.network.name,
    deployer: deployer.address
  };

  const outputPath = path.join(__dirname, "../deployed-addresses.json");
  fs.writeFileSync(outputPath, JSON.stringify(addresses, null, 2));
  console.log("Addresses saved to:", outputPath);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
