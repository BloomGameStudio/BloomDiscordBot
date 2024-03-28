import json

def modify_json():
    with open('data/ongoing_votes.json', 'r+') as f:
        data = json.load(f)
        for key in data:
            data[key]['draft']['background'] = "**Definitions**\nSnapshot - A service to facilitate off-chain governance which uses on-chain tokens for quorum and votes\n\n**Background**\nSince development began on Bloom in 2022, there has been an active effort to collectively decide things, which was formalized with per-member voting in a Discord server to date. There have been 35 general proposals and 26 budgetary proposals in this time, refining and establishing a generally satiating, agreeable system that can now be further canonized by moving consensus to Snapshot.\n\nFurther considerations will be necessary and embarked upon when we again transition from soul-bound Arbitrum tokens to a liquid ERC-20, likely named $hue.\n\n---\n\nAs a starting point, Bloom governance will be guided by cascaded governance proposals, with the base, autological proposal being this one. For the time being, proposals will be branched into two main categories, which can be branched further, but will not have distinct proposal syntax and iteration. That is to say, each proposal # is subsequent to the prior within its own primary branch. The two proposal types are:\n\nBloom General Proposals (BGP)\nBloom Budgetary Proposals (BBP)\n\nTo distinguish these two, it is actually easier to define BBPs first. Budgetary Proposals will entail financial structuring, imbursements, bounties, hiring, termination, and so forth. If it affects Bloom's treasury (treasury.bloomstudio.eth), assets collectively held by the studio, or how we organize around these assets, a BBP is in order. Everything else falls under BGPs, such as this proposal.\n\nAn initial quorum of 25% for all Snapshot votes will be necessary for a vote to be considered valid. This quorum will be based on emitted quantity at time of vote. A winning choice must also receive 2/3 (~67%) of participating vote. \n\nInitial contributor tokens eligible for voting:\nangelXP (Arbitrum address: 0x206d247f61cb82b9711318381cdb7bc5039d2a2c)\nbountyXP (Arbitrum address: 0x4cd06ada7d8564830018000d784c69bd542b1e6a)\nunitXP (Arbitrum address: 0x57d3a929fdc4faf1b35e7092d9dee7af097afb6a)"
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

if __name__ == "__main__":
    modify_json()