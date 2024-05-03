def getMinQty(tokenUSDT) : 
    
    minQtyDict= {'1000SATSUSDT': 1.0, 'SPELLUSDT': 1.0, 'DENTUSDT': 1.0, 'LEVERUSDT': 1.0, 'REEFUSDT': 1.0, 'HOTUSDT': 1.0, 'MBLUSDT': 1.0, 'XVGUSDT': 1.0, 'SLPUSDT': 1.0, '1000PEPEUSDT': 1.0, 'RSRUSDT': 1.0, 'KEYUSDT': 1.0, 'STMXUSDT': 1.0, 'IOSTUSDT': 1.0, 'AMBUSDT': 1.0, 'LINAUSDT': 1.0, 'DGBUSDT': 1.0, 'JASMYUSDT': 1.0, 'CKBUSDT': 1.0, '1000BONKUSDT': 1.0, 'TLMUSDT': 1.0, 'RVNUSDT': 1.0, '1000SHIBUSDT': 1.0, 'USTCUSDT': 1.0, 'ONEUSDT': 1.0, 'CELRUSDT': 1.0, 'ZILUSDT': 1.0, 'BEAMXUSDT': 1.0, 'TUSDT': 1.0, 'MEMEUSDT': 1.0, 'PEOPLEUSDT': 1.0, 'ACHUSDT': 1.0, 'ORBSUSDT': 1.0, 'VETUSDT': 1.0, 'ANKRUSDT': 1.0, 'SNTUSDT': 1.0, 'XEMUSDT': 1.0, 'GALAUSDT': 1.0, '1000XECUSDT': 1.0, 'STPTUSDT': 1.0, 'IOTXUSDT': 1.0, 'ARPAUSDT': 1.0, 'RENUSDT': 1.0, 'WAXPUSDT': 1.0, 'MDTUSDT': 1.0, 'SKLUSDT': 1.0, 'TRUUSDT': 1.0, 'HBARUSDT': 1.0, 'LOOMUSDT': 1.0, 'TRXUSDT': 1.0, 'IDEXUSDT': 1.0, 'FLMUSDT': 1.0, 'XLMUSDT': 1.0, 'TOKENUSDT': 1.0, 'CHZUSDT': 1.0, 'NKNUSDT': 1.0, 'ASTRUSDT': 1.0, 'OXTUSDT': 1.0, 'ROSEUSDT': 1.0, 'KASUSDT': 1.0, 'ALPHAUSDT': 1.0, '1000LUNCUSDT': 1.0, 'DOGEUSDT': 1.0, 'ATAUSDT': 1.0, 'COTIUSDT': 1.0, 'OGNUSDT': 1.0, '1000FLOKIUSDT': 1.0, 'DARUSDT': 0.1, 'RIFUSDT': 1.0, 'ALGOUSDT': 0.1, 'DODOXUSDT': 1.0, '1000RATSUSDT': 1.0, 'KLAYUSDT': 0.1, 'AUDIOUSDT': 1.0, 'GMTUSDT': 1.0, 'ICXUSDT': 1.0, 'CTSIUSDT': 1.0, 'BATUSDT': 0.1, 'IOTAUSDT': 0.1, 'RDNTUSDT': 1.0, 'STEEMUSDT': 1.0, 'ONTUSDT': 0.1, 'BIGTIMEUSDT': 1.0, 'POWRUSDT': 1.0, 'BLZUSDT': 1.0, 'LRCUSDT': 1.0, 'GRTUSDT': 1.0, 'C98USDT': 1.0, 'POLYXUSDT': 1.0, 'ONGUSDT': 1.0, 'BAKEUSDT': 1.0, 'HFTUSDT': 1.0, 'SXPUSDT': 0.1, 'DUSKUSDT': 1.0, 'WOOUSDT': 1.0, 'BNXUSDT': 0.1, 'ENJUSDT': 1.0, 'CHRUSDT': 1.0, 'CFXUSDT': 1.0, 'GLMRUSDT': 1.0, 'BICOUSDT': 1.0, '1INCHUSDT': 1.0, 'BLURUSDT': 1.0, 'MAVUSDT': 1.0, 'ADAUSDT': 1.0, 'SANDUSDT': 1.0, 'MANAUSDT': 1.0, 'XRPUSDT': 0.1, 'CRVUSDT': 0.1, 'STORJUSDT': 1.0, 'SFPUSDT': 1.0, 'STGUSDT': 1.0, 'KNCUSDT': 1.0, 'BELUSDT': 1.0, 'CTKUSDT': 1.0, 'USDCUSDT': 1.0, 'JOEUSDT': 1.0, 'YGGUSDT': 1.0, 'BNTUSDT': 1.0, 'SEIUSDT': 1.0, 'PYTHUSDT': 1.0, 'ZRXUSDT': 0.1, 'KAVAUSDT': 0.1, 'COMBOUSDT': 0.1, 'FTMUSDT': 1.0, 'MATICUSDT': 1.0, 'OCEANUSDT': 1.0, 'MINAUSDT': 1.0, 'AGIXUSDT': 1.0, 'IDUSDT': 1.0, 'EDUUSDT': 1.0, 'HIFIUSDT': 1.0, 'ARKUSDT': 1.0, 'NTRNUSDT': 1.0, 'EOSUSDT': 0.1, 'OMGUSDT': 0.1, 'CELOUSDT': 0.1, 'MAGICUSDT': 0.1, 'LUNA2USDT': 1.0, 'AGLDUSDT': 1.0, 'FRONTUSDT': 1.0, 'TWTUSDT': 1.0, 'SUPERUSDT': 1.0, 'XTZUSDT': 0.1, 'FLOWUSDT': 0.1, 'LQTYUSDT': 0.1, 'LITUSDT': 0.1, 'HOOKUSDT': 0.1, 'PERPUSDT': 0.1, 'SUSHIUSDT': 1.0, 'MTLUSDT': 1.0, 'APEUSDT': 1.0, 'ARBUSDT': 0.1, 'SUIUSDT': 0.1, 'ALICEUSDT': 0.1, 'GTCUSDT': 0.1, 'HIGHUSDT': 0.1, 'BANDUSDT': 0.1, 'MASKUSDT': 1.0, 'IMXUSDT': 1.0, 'LDOUSDT': 1.0, 'CVXUSDT': 1.0, 'FETUSDT': 1.0, 'PHBUSDT': 1.0, 'STXUSDT': 1.0, 'UMAUSDT': 1.0, 'RADUSDT': 1.0, 'PENDLEUSDT': 1.0, 'ARKMUSDT': 1.0, 'CAKEUSDT': 1.0, 'ETHWUSDT': 1.0, 'JTOUSDT': 1.0, 'THETAUSDT': 0.1, 'DYDXUSDT': 0.1, 'WAVESUSDT': 0.1, 'API3USDT': 0.1, 'RLCUSDT': 0.1, 'OPUSDT': 0.1, 'QTUMUSDT': 0.1, 'BONDUSDT': 0.1, 'SNXUSDT': 0.1, 'BALUSDT': 0.1, 'RUNEUSDT': 1.0, 'SOLUSDT': 1.0, 'UNIUSDT': 1.0, 'AVAXUSDT': 1.0, 'NEARUSDT': 1.0, 'AXSUSDT': 1.0, 'GALUSDT': 1.0, 'ICPUSDT': 1.0, 'WLDUSDT': 1.0, 'TIAUSDT': 1.0, 'BADGERUSDT': 1.0, 'UNFIUSDT': 0.1, 'GASUSDT': 0.1, 'FXSUSDT': 0.1, 'DOTUSDT': 0.1, 'FILUSDT': 0.1, 'ANTUSDT': 0.1, 'RNDRUSDT': 0.1, 'ATOMUSDT': 0.01, 'ZENUSDT': 0.1, 'APTUSDT': 0.1, 'BLUEBIRDUSDT': 0.1, 'XVSUSDT': 0.1, 'CYBERUSDT': 0.1, 'NEOUSDT': 0.01, 'LPTUSDT': 0.1, 'ENSUSDT': 0.1, 'AUCTIONUSDT': 0.01, 'KSMUSDT': 0.1, 'ARUSDT': 0.1, 'INJUSDT': 0.1, 'NMRUSDT': 0.1, 'ZECUSDT': 0.001, 'DASHUSDT': 0.001, 'GMXUSDT': 0.01, 'TRBUSDT': 0.1, 'EGLDUSDT': 0.1, 'AAVEUSDT': 0.1, 'QNTUSDT': 0.1, 'BSVUSDT': 0.1, 'ORDIUSDT': 0.1, 'ILVUSDT': 0.1, 'SSVUSDT': 0.01, 'COMPUSDT': 0.001, 'XMRUSDT': 0.001, 'BNBUSDT': 0.01, 'FOOTBALLUSDT': 0.01, 'DEFIUSDT': 0.001, 'BTCDOMUSDT': 0.001, 'MKRUSDT': 0.001, 'YFIUSDT': 0.001, 'SRMUSDT': 1.0, 'HNTUSDT': 1.0, 'TOMOUSDT': 1.0, 'CVCUSDT': 1.0, 'BTSUSDT': 1.0, 'SCUSDT': 1.0, 'STRAXUSDT': 1.0, 'AIUSDT': 1.0, 'XAIUSDT': 1.0, 'LSKUSDT': 1.0, 'ALTUSDT': 1.0, 'JUPUSDT': 1.0, 'ZETAUSDT': 1.0, 'PIXELUSDT': 1.0, 'GLMUSDT': 1.0, 'MYROUSDT': 1.0, 'VANRYUSDT': 1.0, 'BOMEUSDT': 1.0, 'BTCSTUSDT': 0.1, 'RAYUSDT': 0.1, 'FTTUSDT': 0.1, 'COCOSUSDT': 0.1, 'NFPUSDT': 0.1, 'WIFUSDT': 0.1, 'MANTAUSDT': 0.1, 'ONDOUSDT': 0.1, 'RONINUSDT': 0.1, 'DYMUSDT': 0.1, 'OMUSDT': 0.1, 'STRKUSDT': 0.1, 'MAVIAUSDT': 0.1, 'PORTALUSDT': 0.1, 'TONUSDT': 0.1, 'AXLUSDT': 0.1, 'AEVOUSDT': 0.1, 'ETHFIUSDT': 0.1, 'ACEUSDT': 0.01, 'MOVRUSDT': 0.01, 'METISUSDT': 0.01, 'BTCUSDT_240329': 0.001, 'ETHUSDT_240329': 0.001, 'BTCUSDT_240628': 0.001, 'ETHUSDT_240628': 0.001, 'LINKUSDT': 0.01, 'ETCUSDT': 0.01, 'LTCUSDT': 0.001, 'BCHUSDT': 0.001, 'ETHUSDT': 0.001, 'BTCUSDT': 0.001}
    return minQtyDict[tokenUSDT]