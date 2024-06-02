import socket
for n in sorted(set([0, 1, 65535, 65536, 65537, 4294967295, 4294967296, 4294967297, 4295032832, 4295032833, 281474976710656, 281474976710657, 281474976776192, 281474976776193, 281479271677952, 281479271677953, 281479271743488, 281479271743489, 18446744073709551616, 18446744073709551617, 18446744073709617152, 18446744073709617153, 18446744078004518912, 18446744078004518913, 18446744078004584448, 18446744078004584449, 18447025548686262272, 18447025548686262273, 18447025548686327808, 18447025548686327809, 18447025552981229568, 18447025552981229569, 18447025552981295104, 18447025552981295105, 1208925819614629174706176, 1208925819614629174706177, 1208925819614629174771712, 1208925819614629174771713, 1208925819614633469673472, 1208925819614633469673473, 1208925819614633469739008, 1208925819614633469739009, 1208925819896104151416832, 1208925819896104151416833, 1208925819896104151482368, 1208925819896104151482369, 1208925819896108446384128, 1208925819896108446384129, 1208925819896108446449664, 1208925819896108446449665, 1208944266358702884257792, 1208944266358702884257793, 1208944266358702884323328, 1208944266358702884323329, 1208944266358707179225088, 1208944266358707179225089, 1208944266358707179290624, 1208944266358707179290625, 1208944266640177860968448, 1208944266640177860968449, 1208944266640177861033984, 1208944266640177861033985, 1208944266640182155935744, 1208944266640182155935745, 1208944266640182156001280, 1208944266640182156001281, 79228162514264337593543950336, 79228162514264337593543950337, 79228162514264337593544015872, 79228162514264337593544015873, 79228162514264337597838917632, 79228162514264337597838917633, 79228162514264337597838983168, 79228162514264337597838983169, 79228162514264619068520660992, 79228162514264619068520660993, 79228162514264619068520726528, 79228162514264619068520726529, 79228162514264619072815628288, 79228162514264619072815628289, 79228162514264619072815693824, 79228162514264619072815693825, 79228162532711081667253501952, 79228162532711081667253501953, 79228162532711081667253567488, 79228162532711081667253567489, 79228162532711081671548469248, 79228162532711081671548469249, 79228162532711081671548534784, 79228162532711081671548534785, 79228162532711363142230212608, 79228162532711363142230212609, 79228162532711363142230278144, 79228162532711363142230278145, 79228162532711363146525179904, 79228162532711363146525179905, 79228162532711363146525245440, 79228162532711363146525245441, 79229371440083952222718656512, 79229371440083952222718656513, 79229371440083952222718722048, 79229371440083952222718722049, 79229371440083952227013623808, 79229371440083952227013623809, 79229371440083952227013689344, 79229371440083952227013689345, 79229371440084233697695367168, 79229371440084233697695367169, 79229371440084233697695432704, 79229371440084233697695432705, 79229371440084233701990334464, 79229371440084233701990334465, 79229371440084233701990400000, 79229371440084233701990400001, 79229371458530696296428208128, 79229371458530696296428208129, 79229371458530696296428273664, 79229371458530696296428273665, 79229371458530696300723175424, 79229371458530696300723175425, 79229371458530696300723240960, 79229371458530696300723240961, 79229371458530977771404918784, 79229371458530977771404918785, 79229371458530977771404984320, 79229371458530977771404984321, 79229371458530977775699886080, 79229371458530977775699886081, 79229371458530977775699951616, 79229371458530977775699951617, 5192296858534827628530496329220096, 5192296858534827628530496329220097, 5192296858534827628530496329285632, 5192296858534827628530496329285633, 5192296858534827628530500624187392, 5192296858534827628530500624187393, 5192296858534827628530500624252928, 5192296858534827628530500624252929, 5192296858534827628811971305930752, 5192296858534827628811971305930753, 5192296858534827628811971305996288, 5192296858534827628811971305996289, 5192296858534827628811975600898048, 5192296858534827628811975600898049, 5192296858534827628811975600963584, 5192296858534827628811975600963585, 5192296858534846075274570038771712, 5192296858534846075274570038771713, 5192296858534846075274570038837248, 5192296858534846075274570038837249, 5192296858534846075274574333739008, 5192296858534846075274574333739009, 5192296858534846075274574333804544, 5192296858534846075274574333804545, 5192296858534846075556045015482368, 5192296858534846075556045015482369, 5192296858534846075556045015547904, 5192296858534846075556045015547905, 5192296858534846075556049310449664, 5192296858534846075556049310449665, 5192296858534846075556049310515200, 5192296858534846075556049310515201, 5192296859743753448145125503926272, 5192296859743753448145125503926273, 5192296859743753448145125503991808, 5192296859743753448145125503991809, 5192296859743753448145129798893568, 5192296859743753448145129798893569, 5192296859743753448145129798959104, 5192296859743753448145129798959105, 5192296859743753448426600480636928, 5192296859743753448426600480636929, 5192296859743753448426600480702464, 5192296859743753448426600480702465, 5192296859743753448426604775604224, 5192296859743753448426604775604225, 5192296859743753448426604775669760, 5192296859743753448426604775669761, 5192296859743771894889199213477888, 5192296859743771894889199213477889, 5192296859743771894889199213543424, 5192296859743771894889199213543425, 5192296859743771894889203508445184, 5192296859743771894889203508445185, 5192296859743771894889203508510720, 5192296859743771894889203508510721, 5192296859743771895170674190188544, 5192296859743771895170674190188545, 5192296859743771895170674190254080, 5192296859743771895170674190254081, 5192296859743771895170678485155840, 5192296859743771895170678485155841, 5192296859743771895170678485221376, 5192296859743771895170678485221377, 5192376086697341892868089873170432, 5192376086697341892868089873170433, 5192376086697341892868089873235968, 5192376086697341892868089873235969, 5192376086697341892868094168137728, 5192376086697341892868094168137729, 5192376086697341892868094168203264, 5192376086697341892868094168203265, 5192376086697341893149564849881088, 5192376086697341893149564849881089, 5192376086697341893149564849946624, 5192376086697341893149564849946625, 5192376086697341893149569144848384, 5192376086697341893149569144848385, 5192376086697341893149569144913920, 5192376086697341893149569144913921, 5192376086697360339612163582722048, 5192376086697360339612163582722049, 5192376086697360339612163582787584, 5192376086697360339612163582787585, 5192376086697360339612167877689344, 5192376086697360339612167877689345, 5192376086697360339612167877754880, 5192376086697360339612167877754881, 5192376086697360339893638559432704, 5192376086697360339893638559432705, 5192376086697360339893638559498240, 5192376086697360339893638559498241, 5192376086697360339893642854400000, 5192376086697360339893642854400001, 5192376086697360339893642854465536, 5192376086697360339893642854465537, 5192376087906267712482719047876608, 5192376087906267712482719047876609, 5192376087906267712482719047942144, 5192376087906267712482719047942145, 5192376087906267712482723342843904, 5192376087906267712482723342843905, 5192376087906267712482723342909440, 5192376087906267712482723342909441, 5192376087906267712764194024587264, 5192376087906267712764194024587265, 5192376087906267712764194024652800, 5192376087906267712764194024652801, 5192376087906267712764198319554560, 5192376087906267712764198319554561, 5192376087906267712764198319620096, 5192376087906267712764198319620097, 5192376087906286159226792757428224, 5192376087906286159226792757428225, 5192376087906286159226792757493760, 5192376087906286159226792757493761, 5192376087906286159226797052395520, 5192376087906286159226797052395521, 5192376087906286159226797052461056, 5192376087906286159226797052461057, 5192376087906286159508267734138880, 5192376087906286159508267734138881, 5192376087906286159508267734204416, 5192376087906286159508267734204417, 5192376087906286159508272029106176, 5192376087906286159508272029106177, 5192376087906286159508272029171712, 5192376087906286159508272029171713, 2**128 - 1,
    (0xffff << 32) - 1,
    (0xffff << 32),
    (0xffff << 32) + 1,
    (0xffff << 32) + (1 << 16) - 1,
    (0xffff << 32) + (1 << 16),
    (0xffff << 32) - (1 << 16) + 1,
    (0xffff << 32) + (1 << 32) - 1,
    (0xffff << 32) + (1 << 32),
])):
    print(f'{n:40} {socket.inet_ntop(socket.AF_INET6, n.to_bytes(16, "big"))}')
