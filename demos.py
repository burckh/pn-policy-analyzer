from km import PetriNet, KarpMillerTree
from parser import parse_petri_net_file

def build_km_tree(pnfile):
    places, init_mark, trans = parse_petri_net_file(pnfile)
    pn = PetriNet(places, trans)

    return KarpMillerTree(pn, init_mark)

def naive_acm_demo():

    km_tree = build_km_tree("./pns/naive_acm.txt")

    # is the ACM enforced?
    found = km_tree.search(lambda m: m["s1_w_o2"] > 0) # can s1 write to o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s2_w_o1"] > 0) # can s2 write to o1?
    assert(not found)
    found = km_tree.search(lambda m: m["s2_r_o2"] > 0) # can s2 read o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_r_o1"] > 0) # can s3 read o1?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_r_o2"] > 0) # can s3 read o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_w_o2"] > 0) # can s3 write to o2?
    assert(not found)

    # can unavailable resources start being used?
    found = km_tree.search(lambda m: 
        m["s1_w_o1"] > 0 and ( # while s1 is writing to o1 (o1 is unavailable)
        (m["s1_can_r_o1"] >= 1 and m["o1"] >= 1) or # can s1 start reading o1?
        (m["s1_can_w_o1"] >= 1 and m["o1"] >= 1) or # can s1 start writing to o1?
        (m["s2_can_r_o1"] >= 1 and m["o1"] >= 1) or # can s2 start reading o1?
        (m["s3_can_w_o1"] >= 1 and m["o1"] >= 1)    # can s3 start writing to o1?
        )
    )
    assert(not found)
    found = km_tree.search( lambda m: 
        m["s2_w_o2"] > 0 and # while s2 is writing to o2 (o2 is unavailable)
        (m["s1_can_r_o2"] >= 1 and m["o2"] >= 1) # can s1 start reading o2?
    )
    assert(not found)

    # are dirty reads possible?
    found = km_tree.search(
        lambda m: m["s1_r_o1"] > 0 and # while s1 is reading o1
        (m["s3_can_w_o1"] >= 1 and m["o1"] >= 1) # can s3 start writing to o1?
    )
    assert(found)
    found = km_tree.search(
        lambda m: m["s1_r_o1"] > 0 and # while s1 is reading o1
        (m["s1_can_w_o1"] >= 1 and m["o1"] >= 1) # can s1 start writing to o1?
    )
    assert(found)

    return

def acm_demo():

    km_tree = build_km_tree("./pns/acm.txt")
    km_tree.print_tree()

    # are concurrent actions on the same object
    # by the same subject possible?
    found = km_tree.search(lambda m: 
        m["s1_r_o1"] > 0 and # s1 is reading o1
        (m["max_conc_all"] >= 1 and m["max_conc_s1_o1"] >= 1 and m["s1_can_w_o1"] >= 1 and m["o1"] >= 1) # s1 can start writing to o1
    )
    assert(not found)

    # are more concurrent actions than 2 possible?
    found = km_tree.search(lambda m: 
        (m["s1_r_o1"] > 0 and m["s2_r_o1"] > 0 and m["s3_w_o1"] > 0) or
        (m["s1_w_o1"] > 0 and m["s2_r_o1"] > 0 and m["s3_w_o1"] > 0) or
        (m["s1_r_o2"] > 0 and m["s2_r_o1"] > 0 and m["s3_w_o1"] > 0) or
        (m["s1_r_o1"] > 0 and m["s2_w_o2"] > 0 and m["s3_w_o1"] > 0) or
        (m["s1_w_o1"] > 0 and m["s2_w_o2"] > 0 and m["s3_w_o1"] > 0) or
        (m["s1_r_o2"] > 0 and m["s2_w_o2"] > 0 and m["s3_w_o1"] > 0)
    )
    assert(not found)

    ## are the naive ACM rules enforced as well?

    # is the ACM enforced?
    found = km_tree.search(lambda m: m["s1_w_o2"] > 0) # can s1 write to o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s2_w_o1"] > 0) # can s2 write to o1?
    assert(not found)
    found = km_tree.search(lambda m: m["s2_r_o2"] > 0) # can s2 read o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_r_o1"] > 0) # can s3 read o1?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_r_o2"] > 0) # can s3 read o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_w_o2"] > 0) # can s3 write to o2?
    assert(not found)

    # can unavailable resources start being used?
    found = km_tree.search(lambda m: 
        m["s1_w_o1"] > 0 and ( # while s1 is writing to o1 (o1 is unavailable)
        (m["s1_can_r_o1"] >= 1 and m["o1"] >= 1) or # can s1 start reading o1?
        (m["s1_can_w_o1"] >= 1 and m["o1"] >= 1) or # can s1 start writing to o1?
        (m["s2_can_r_o1"] >= 1 and m["o1"] >= 1) or # can s2 start reading o1?
        (m["s3_can_w_o1"] >= 1 and m["o1"] >= 1)    # can s3 start writing to o1?
        )
    )
    assert(not found)
    found = km_tree.search( lambda m: 
        m["s2_w_o2"] > 0 and # while s2 is writing to o2 (o2 is unavailable)
        (m["s1_can_r_o2"] >= 1 and m["o2"] >= 1) # can s1 start reading o2?
    )
    assert(not found)
    
    return

def rbac_demo():

    km_tree = build_km_tree("./pns/rbac.txt")

    # can s3 revoke or grant rights?
    found = km_tree.search(lambda m:
        m["s3_is_adm"] >= 1 and ( # common condition
        m["s1_can_r_o1"] >= 1 or m["s1_can_w_o1"] >= 1 or
        m["safe_s1_r_o1"] >= 1 or m["safe_s1_w_o1"] >= 1 or
        m["s1_can_r_o2"] >= 1 or m["s1_can_w_o2"] >= 1 or
        m["safe_s1_r_o2"] >= 1 or m["safe_s1_w_o2"] >= 1 or
        m["s2_can_r_o1"] >= 1 or m["s2_can_w_o1"] >= 1 or
        m["safe_s2_r_o1"] >= 1 or m["safe_s2_w_o1"] >= 1 or
        m["s2_can_r_o2"] >= 1 or m["s2_can_w_o2"] >= 1 or
        m["safe_s2_r_o2"] >= 1 or m["safe_s2_w_o2"] >= 1
        ) 
    )
    assert(not found)

    # are the ACM places 1-bounded?
    found = km_tree.search(lambda m:
        m["s1_can_r_o1"] > 1 or m["s1_can_w_o1"] > 1 or 
        m["s1_can_r_o2"] > 1 or m["s1_can_w_o2"] > 1 or 
        m["s2_can_r_o1"] > 1 or m["s2_can_w_o1"] > 1 or 
        m["s2_can_r_o2"] > 1 or m["s2_can_w_o2"] > 1 or 
        m["s3_can_r_o1"] > 1 or m["s3_can_w_o1"] > 1 or 
        m["s3_can_r_o2"] > 1 or m["s3_can_w_o2"] > 1
    )
    assert(not found)
    return

def blp_demo():

    km_tree = build_km_tree("./pns/blp.txt")

    # is the ACM still enforced?
    found = km_tree.search(lambda m: m["s1_w_o2"] > 0) # can s1 write to o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s2_w_o1"] > 0) # can s2 write to o1?
    assert(not found)
    found = km_tree.search(lambda m: m["s2_r_o2"] > 0) # can s2 read o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_r_o1"] > 0) # can s3 read o1?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_r_o2"] > 0) # can s3 read o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_w_o2"] > 0) # can s3 write to o2?
    assert(not found)

    # is the NRU rule enforced?
    found = km_tree.search(lambda m: m["s1_r_o2"] > 0) # can s1 read o2?
    assert(not found)

    # is the NWD rule enforced?
    found = km_tree.search(lambda m: m["s1_r_o2"] > 0) # can s1 write to o1?
    assert(not found)

    return

def biba_demo():

    km_tree = build_km_tree("./pns/biba.txt")

    # is the ACM still enforced?
    found = km_tree.search(lambda m: m["s1_w_o2"] > 0) # can s1 write to o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s2_w_o1"] > 0) # can s2 write to o1?
    assert(not found)
    found = km_tree.search(lambda m: m["s2_r_o2"] > 0) # can s2 read o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_r_o1"] > 0) # can s3 read o1?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_r_o2"] > 0) # can s3 read o2?
    assert(not found)
    found = km_tree.search(lambda m: m["s3_w_o2"] > 0) # can s3 write to o2?
    assert(not found)

    # is the NRD rule enforced?
    found = km_tree.search(lambda m: m["s1_r_o1"] > 0) # can s1 read o1?
    assert(not found)
    
    # is the NWU rule enforced?
    found = km_tree.search(lambda m: m["s2_w_o2"] > 0) # can s2 write to o2?
    assert(not found)

    # is the system strongly tranquil?
    found = km_tree.search(lambda m: 
        m["s1_geq_o1"] != 1 or
        m["s1_leq_o1"] != 0 or
        m["s1_geq_o2"] != 0 or
        m["s1_leq_o2"] != 1 or
        m["s2_geq_o1"] != 1 or
        m["s2_leq_o1"] != 1 or
        m["s2_geq_o2"] != 0 or
        m["s2_leq_o2"] != 1 or
        m["s3_geq_o1"] != 1 or
        m["s3_leq_o1"] != 1 or
        m["s3_geq_o2"] != 0 or
        m["s3_leq_o2"] != 1
    )
    assert(not found)

    # can violations of weak tranquility be detected?
    # s1 reads o2, then is upgraded to a level higher than it
    found = km_tree.search(lambda m: m["s1_leq_o2"] == 0 and m["s1_tran_o2"] > 0, return_path=True)
    found = [f for f in found if "s1_strt_r_o2" not in f[1]]
    assert(not found)

    # s2 reads o1, etc.
    found = km_tree.search(lambda m: m["s2_leq_o1"] == 0 and m["s2_tran_o1"] > 0, return_path=True)
    found = [f for f in found if "s2_strt_r_o1" not in f[1]]
    assert(not found)

    found = km_tree.search(lambda m: m["s2_leq_o2"] == 0 and m["s2_tran_o2"] > 0, return_path=True)
    found = [f for f in found if "s2_strt_r_o2" not in f[1]]
    assert(not found)

    found = km_tree.search(lambda m: m["s3_leq_o1"] == 0 and m["s3_tran_o1"] > 0, return_path=True)
    found = [f for f in found if "s2_strt_r_o1" not in f[1]]
    assert(not found)

    found = km_tree.search(lambda m: m["s3_leq_o2"] == 0 and m["s3_tran_o2"] > 0, return_path=True)
    found = [f for f in found if "s3_strt_r_o2" not in f[1]]
    assert(not found)

    return

def cw_demo():

    km_tree = build_km_tree("./pns/cw.txt")

    # running an IVP on a CDI certifies it as valid
    found = km_tree.search(lambda m: m["o1_is_cdi"] > 0 and m["o1_is_val"] == 0, return_path=True)
    found = [f for f in found if "i1_cert_o1" in f[1]]
    assert(not found)
    found = km_tree.search(lambda m: m["o2_is_cdi"] > 0 and m["o2_is_val"] == 0, return_path=True)
    found = [f for f in found if "i1_cert_o2" in f[1]]
    assert(not found)

    # running a TP on a UDI makes it a CDI
    found = km_tree.search(lambda m: m["o2_is_udi"] == 1 and m["o2_is_cdi"] == 0, return_path=True)
    found = [f for f in found if "run_tp1_on_o2" in f[1] or "run_tp2_on_o2" in f[1]]
    assert(not found)

    # users cannot run a TP on a DI unless they are authorized
    found = km_tree.search(lambda m: 
        (m["s1_is_auth"] > 0 and m["tp1_is_val"] > 0 and m["s1_auth_tp1_on_o2"] > 0 and m["o2_lock"] > 0) or # s1 cannot run TP1 on o2
        (m["s1_is_auth"] > 0 and m["tp2_is_val"] > 0 and m["s1_auth_tp2_on_o1"] > 0 and m["o1_lock"] > 0) or # s1 cannot run TP2 on o1
        (m["s1_is_auth"] > 0 and m["tp2_is_val"] > 0 and m["s1_auth_tp2_on_o2"] > 0 and m["o2_lock"] > 0) or # etc.
        (m["s2_is_auth"] > 0 and m["tp1_is_val"] > 0 and m["s2_auth_tp1_on_o1"] > 0 and m["o1_lock"] > 0) or
        (m["s2_is_auth"] > 0 and m["tp2_is_val"] > 0 and m["s2_auth_tp2_on_o1"] > 0 and m["o1_lock"] > 0) or
        (m["s2_is_auth"] > 0 and m["tp2_is_val"] > 0 and m["s2_auth_tp2_on_o2"] > 0 and m["o2_lock"] > 0) or
        (m["s3_is_auth"] > 0 and m["tp1_is_val"] > 0 and m["s3_auth_tp1_on_o1"] > 0 and m["o1_lock"] > 0) or
        (m["s3_is_auth"] > 0 and m["tp1_is_val"] > 0 and m["s3_auth_tp1_on_o2"] > 0 and m["o2_lock"] > 0)
    )
    assert(not found)

    # users cannot run a TPs unless they are authenticated
    found = km_tree.search(lambda m:
        (m["s1_is_auth"] > 0 and m["tp1_is_val"] > 0 and m["s1_auth_tp1_on_o1"] > 0 and m["o1_lock"] > 0 and m["s1_is_auth"] == 0) or
        (m["s2_is_auth"] > 0 and m["tp1_is_val"] > 0 and m["s2_auth_tp1_on_o2"] > 0 and m["o2_lock"] > 0 and m["s2_is_auth"] == 0) or
        (m["s3_is_auth"] > 0 and m["tp2_is_val"] > 0 and m["s3_auth_tp2_on_o1"] > 0 and m["o1_lock"] > 0 and m["s3_is_auth"] == 0) or
        (m["s3_is_auth"] > 0 and m["tp2_is_val"] > 0 and m["s3_auth_tp2_on_o2"] > 0 and m["o2_lock"] > 0 and m["s3_is_auth"] == 0)
    )
    assert(not found)

    return