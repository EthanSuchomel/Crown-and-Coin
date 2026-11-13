"""The board Mammal numbers from browser commit 5d2cd9e, ported to the Godot version.
Rhino 12 damage, Porcupine 8 health with quills (a melee hit that lands on it pricks the attacker for 1),
no Procoptodon in the Mammal barracks (its numbers stay so old saves load). Usage: python3 p1_mammals.py PROJ"""
import sys
from common import F, T
P = sys.argv[1]

# data/units.json
f = F(P + '/data/units.json')
f.rep('''		"name": "Porcupine",
		"hp": 16,''', '''		"name": "Porcupine",
		"hp": 8,''', raw=True)
f.rep('''		"hk": "archer",
		"mammal": true,
		"note": "Shooter: quills, like Archer arrows. Hits flyers (misses 20%)"''',
      '''		"hk": "archer",
		"thorns": 1,
		"mammal": true,
		"note": "Shooter: quills, like Archer arrows. Hits flyers (misses 20%). Its quills prick back: a melee attacker that lands a hit on it takes 1 damage"''', raw=True)
f.rep('''		"name": "Rhino",
		"hp": 28,
		"dmg": 15,''', '''		"name": "Rhino",
		"hp": 28,
		"dmg": 12,''', raw=True)
f.rep('''		"name": "Procoptodon",''', '''		"_note": "taken out of the game (2026-11-07); its numbers stay so old saved games still load",
		"name": "Procoptodon",''', raw=True)
f.save()

# data/factions.json: the Mammal barracks trains Gorilla, Porcupine, Rhino
f = F(P + '/data/factions.json')
f.rep('''				"rhino",
				"kanga"
			],''', '''				"rhino"
			],''', raw=True)
f.save()

# data/rules.json: no Procoptodon unlock, not a Watering Hole unit
f = F(P + '/data/rules.json')
f.rep('''		"rhino": 1,
		"kanga": 2,
''', '''		"rhino": 1,
''', raw=True)
f.rep('''			"rhino",
			"kanga",
			"gbat",''', '''			"rhino",
			"gbat",''', raw=True)
f.save()

# data/upgrades.json: Watering Hole texts
f = F(P + '/data/upgrades.json')
f.rep('Rhinos, Procoptodons, Desmodus and Palaeoloxodons', 'Rhinos, Desmodus and Palaeoloxodons', n=2, raw=True)
f.save()

# scripts/ui/main.gd: Watering Hole button and barracks level notes, as in the browser
f = F(P + '/scripts/ui/main.gd')
f.rep('"Rhinos, Procoptodons, Desmodus and Palaeoloxodons cost 5 less here"', '"Rhinos, Desmodus and Palaeoloxodons cost 5 less here"', raw=True)
f.rep('["Unlocks the Megaraptor and Robot Knight", "Unlocks the Longbow",', '["Unlocks the Megaraptor, Robot Knight and Rhino", "Unlocks the Longbow",', raw=True)
f.save()

# scripts/rules/combat.gd: Porcupine quills in board battles (browser strike()/fightBattle())
f = F(P + '/scripts/rules/combat.gd')
f.rep('''        "out": {"dmg": {}, "wall": 0.0, "any": false, "shield": 0.0, "stun": {}},''',
      '''        "out": {"dmg": {}, "wall": 0.0, "any": false, "shield": 0.0, "stun": {}, "recoil": {}},   # recoil: damage back on this side's own units (Porcupine quills)''')
f.rep('''                st.out.dmg[tk] = float(st.out.dmg.get(tk, 0.0)) + dd
                st.left[tk] = float(st.left[tk]) - dd
                pool -= dd / per_m''', '''                st.out.dmg[tk] = float(st.out.dmg.get(tk, 0.0)) + dd
                st.left[tk] = float(st.left[tk]) - dd
                pool -= dd / per_m
                if float(unit(tk).get("thorns", 0)) > 0.0 and dd > 0.0:   # trampling Porcupines pricks the Rhinos
                    var one_r: float = (float(RC.dmg) + float(RC.next) * (hits - 1)) / hits * m
                    st.out.recoil["rhino"] = float(st.out.recoil.get("rhino", 0.0)) + dd / one_r * float(unit(tk).thorns)''')
f.rep('''        var w0: Dictionary = U.duplicate(true)
''', '''        var w0: Dictionary = U.duplicate(true)
        w0["key"] = k
''')
f.rep('''        out.dmg[tk] = float(out.dmg.get(tk, 0.0)) + dd
        st.left[tk] = float(st.left[tk]) - dd
        time -= use
''', '''        out.dmg[tk] = float(out.dmg.get(tk, 0.0)) + dd
        st.left[tk] = float(st.left[tk]) - dd
        time -= use
        # Porcupine quills: every melee hit that lands pricks the attacker for 1 (shots, lasers, rockets and magic don't)
        if float(T2.get("thorns", 0)) > 0.0 and w.has("key") and dd > 0.0 and not w.get("rng", false) and not w.has("beam") and String(w.get("hk", "")) != "gunship" and String(w.get("hk", "")) != "magic":
            var w1: Dictionary = weapon.duplicate()
            w1.shots = 1
            w1.charged = false
            for x in ["multi", "missAir", "missHeavy"]:
                w1.erase(x)
            w1.sweep = false
            w1.cleave = false
            var T1: Dictionary = T2.duplicate()
            T1.erase("dodge")
            T1.erase("deflect")
            var one: float = _hit_one(st, w1, T1, tk)
            if one > 0.0:
                out.recoil[w.key] = float(out.recoil.get(w.key, 0.0)) + dd / one * float(T2.thorns)
''')
f.rep('''        _apply(D, hits_on_d.dmg)
        _apply(A, hits_on_a.dmg)
''', '''        _apply(D, hits_on_d.dmg)
        _apply(A, hits_on_a.dmg)
        # Porcupine quills prick back the melee attackers that hit them
        var rc_a: Dictionary = hits_on_d.recoil
        var rc_d: Dictionary = hits_on_a.recoil
        if bool(o.get("a_arm", false)):
            for k in rc_a:
                rc_a[k] = float(rc_a[k]) / arm_hp
        if bool(o.get("d_arm", false)):
            for k in rc_d:
                rc_d[k] = float(rc_d[k]) / arm_hp
        _apply(A, rc_a)
        _apply(D, rc_d)
''')
f.save()

# scripts/rules/test_rules.gd: checks
f = F(P + '/scripts/rules/test_rules.gd')
f.rep('"_test_three", "_test_robots"]', '"_test_three", "_test_robots", "_test_mammal_numbers"]', raw=True)
i = f.s.find('\nfunc ', f.s.find('func _ready'))
assert i > 0
f.s = f.s[:i] + '\n' + T('''
func _test_mammal_numbers() -> void:
    var u: Dictionary = GameData.units
    check("mammals: Porcupine 8 health with quills", int(u.porc.hp) == 8 and int(u.porc.get("thorns", 0)) == 1)
    check("mammals: Rhino 12 damage", int(u.rhino.dmg) == 12)
    check("mammals: the barracks trains Gorilla, Porcupine, Rhino", GameData.factions.mammals.training.barracks == ["ape", "porc", "rhino"])
    check("mammals: no Procoptodon to unlock or discount", not GameData.rules.barracks_unlocks.has("kanga") and not GameData.rules.mammals.wh_units.has("kanga"))
    # quills: Gorillas (melee) lose more health against Porcupines with quills; Archers (shots) don't
    var avg: Dictionary = {"avg": true}
    var with_q: Dictionary = CombatRules.fight({"ape": 6}, {"porc": 6}, avg)
    var arch_q: Dictionary = CombatRules.fight({"rarch": 6}, {"porc": 6}, avg)
    var tr_q: Dictionary = CombatRules.fight({"rhino": 2}, {"porc": 6}, avg)
    u.porc.thorns = 0
    var no_q: Dictionary = CombatRules.fight({"ape": 6}, {"porc": 6}, avg)
    var arch_n: Dictionary = CombatRules.fight({"rarch": 6}, {"porc": 6}, avg)
    var tr_n: Dictionary = CombatRules.fight({"rhino": 2}, {"porc": 6}, avg)
    u.porc.thorns = 1
    check("mammals: quills prick Gorillas in board battles", float(with_q.a_hp) < float(no_q.a_hp) - 0.5, "%s vs %s" % [with_q.a_hp, no_q.a_hp])
    check("mammals: quills don't prick shooters", absf(float(arch_q.a_hp) - float(arch_n.a_hp)) < 0.01, "%s vs %s" % [arch_q.a_hp, arch_n.a_hp])
    check("mammals: trampling Porcupines pricks the Rhinos", float(tr_q.a_hp) < float(tr_n.a_hp) - 0.5, "%s vs %s" % [tr_q.a_hp, tr_n.a_hp])
''') + f.s[i:]
f.save()
print('ok')
