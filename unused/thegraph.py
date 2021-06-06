QUICKSWAP_GRAPH_ADDRESS = "https://api.thegraph.com/subgraphs/name/apyvision/quickswap-subgraph"

test_uni_lp_query = """
{
  user(id : "0x00275072a952f7731d507dc5dec9bcb27c13cfc3") {
    id
    liquidityPositions {
      liquidityTokenBalance
      pair {
        token0 {
          symbol
        }
        token0Price
        token1 {
          symbol
        }
        token1Price
        reserve0
        reserve1
        totalSupply
      }
    }
  }
}
"""