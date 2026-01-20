// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AgriDAO {
    struct Proposal {
        uint256 id;
        address proposer;
        string description;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 endTime;
        bool executed;
        mapping(address => bool) hasVoted;
    }

    struct Member {
        bool isMember;
        uint256 votingPower;
        uint256 joinedAt;
    }

    mapping(address => Member) public members;
    mapping(uint256 => Proposal) public proposals;
    uint256 public proposalCount;
    uint256 public memberCount;
    
    uint256 public constant VOTING_PERIOD = 3 days;
    uint256 public constant MIN_VOTING_POWER = 1;

    event MemberAdded(address indexed member, uint256 votingPower);
    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, string description);
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 indexed proposalId);

    modifier onlyMember() {
        require(members[msg.sender].isMember, "Not a member");
        _;
    }

    function joinDAO() external {
        require(!members[msg.sender].isMember, "Already a member");
        
        members[msg.sender] = Member({
            isMember: true,
            votingPower: MIN_VOTING_POWER,
            joinedAt: block.timestamp
        });
        memberCount++;
        
        emit MemberAdded(msg.sender, MIN_VOTING_POWER);
    }

    function createProposal(string memory description) external onlyMember returns (uint256) {
        uint256 proposalId = proposalCount++;
        Proposal storage proposal = proposals[proposalId];
        
        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.description = description;
        proposal.endTime = block.timestamp + VOTING_PERIOD;
        proposal.executed = false;
        
        emit ProposalCreated(proposalId, msg.sender, description);
        return proposalId;
    }

    function vote(uint256 proposalId, bool support) external onlyMember {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp < proposal.endTime, "Voting ended");
        require(!proposal.hasVoted[msg.sender], "Already voted");
        
        uint256 weight = members[msg.sender].votingPower;
        proposal.hasVoted[msg.sender] = true;
        
        if (support) {
            proposal.forVotes += weight;
        } else {
            proposal.againstVotes += weight;
        }
        
        emit VoteCast(proposalId, msg.sender, support, weight);
    }

    function executeProposal(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp >= proposal.endTime, "Voting not ended");
        require(!proposal.executed, "Already executed");
        require(proposal.forVotes > proposal.againstVotes, "Proposal rejected");
        
        proposal.executed = true;
        emit ProposalExecuted(proposalId);
    }

    function getProposal(uint256 proposalId) external view returns (
        address proposer,
        string memory description,
        uint256 forVotes,
        uint256 againstVotes,
        uint256 endTime,
        bool executed
    ) {
        Proposal storage proposal = proposals[proposalId];
        return (
            proposal.proposer,
            proposal.description,
            proposal.forVotes,
            proposal.againstVotes,
            proposal.endTime,
            proposal.executed
        );
    }

    function hasVoted(uint256 proposalId, address voter) external view returns (bool) {
        return proposals[proposalId].hasVoted[voter];
    }

    function getMember(address account) external view returns (bool isMember, uint256 votingPower, uint256 joinedAt) {
        Member memory member = members[account];
        return (member.isMember, member.votingPower, member.joinedAt);
    }
}
