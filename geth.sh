#!/bin/sh
geth --datadir datadir --networkid 1010 --bootnodes enode://3c824785860af1903820f1e58428dca1db41ea1fc4b28748b243894a393b0e0838b8201215a63d6513f3d36b78a54489ce3a81ac673a7eb81258a0794a6d4bf4@crosschain.musalbas.com:0?discport=30301 "$@"
