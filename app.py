import random
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="용사의 모험 RPG", page_icon="⚔️")

# ---------------------------------------------------------
# 1. 게임 상태 초기화 (Session State)
# ---------------------------------------------------------
if "hp" not in st.session_state:
    st.session_state.hp = 100
if "max_hp" not in st.session_state:
    st.session_state.max_hp = 100
if "gold" not in st.session_state:
    st.session_state.gold = 20
if "level" not in st.session_state:
    st.session_state.level = 1
if "exp" not in st.session_state:
    st.session_state.exp = 0
if "scene" not in st.session_state:
    st.session_state.scene = "town"
if "logs" not in st.session_state:
    st.session_state.logs = ["모험의 세계에 오신 것을 환영합니다!"]
if "monster" not in st.session_state:
    st.session_state.monster = None


def add_log(text):
    """게임 일지에 기록 추가"""
    st.session_state.logs.append(text)


def reset_game():
    """게임 초기화"""
    st.session_state.hp = 100
    st.session_state.max_hp = 100
    st.session_state.gold = 20
    st.session_state.level = 1
    st.session_state.exp = 0
    st.session_state.scene = "town"
    st.session_state.monster = None
    st.session_state.logs = ["새로운 모험이 시작되었습니다."]


# ---------------------------------------------------------
# 2. 게임 상단 상태창
# ---------------------------------------------------------
st.title("⚔️ 용사의 모험 (Streamlit RPG)")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("레벨", f"Lv. {st.session_state.level}")
with col2:
    st.metric("체력", f"{st.session_state.hp} / {st.session_state.max_hp}")
with col3:
    st.metric("골드", f"{st.session_state.gold} G")
with col4:
    st.metric("경험치", f"{st.session_state.exp} / {st.session_state.level * 50}")

st.divider()

# ---------------------------------------------------------
# 3. 게임 진행 로직 및 화면 구성
# ---------------------------------------------------------

# [게임 오버 처리]
if st.session_state.hp <= 0:
    st.error("💀 체력이 0이 되어 쓰러졌습니다... 게임 오버!")
    if st.button("🔄 처음부터 다시 시작"):
        reset_game()
        st.rerun()

# [정상 게임 진행]
else:
    # ------------------ [마을] ------------------
    if st.session_state.scene == "town":
        st.subheader("🏘️ 평화로운 마을")
        st.write("마을에서 모험 준비를 하거나 던전으로 떠날 수 있습니다.")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🌲 던전 탐험하러 가기"):
                st.session_state.scene = "dungeon"
                add_log("어두운 던전에 들어섰습니다.")
                st.rerun()

        with col_b:
            if st.button("🏨 여관에서 쉬기 (10 Gold)"):
                if st.session_state.gold >= 10:
                    st.session_state.gold -= 10
                    st.session_state.hp = st.session_state.max_hp
                    add_log("여관에서 푹 쉬어 체력을 모두 회복했습니다!")
                else:
                    add_log("골드가 부족하여 여관을 이용할 수 없습니다.")
                st.rerun()

    # ------------------ [던전] ------------------
    elif st.session_state.scene == "dungeon":
        st.subheader("🌲 위험한 던전")

        # 몬스터 미조우 시 무작위 생성
        if st.session_state.monster is None:
            monsters = [
                {"name": "슬라임", "hp": 30, "atk": 8, "exp": 20, "gold": 10},
                {"name": "고블린", "hp": 50, "atk": 15, "exp": 35, "gold": 20},
                {"name": "오크", "hp": 80, "atk": 22, "exp": 60, "gold": 35},
            ]
            st.session_state.monster = random.choice(monsters).copy()
            add_log(f"야생의 {st.session_state.monster['name']}(이)가 나타났다!")

        monster = st.session_state.monster
        st.warning(
            f"👾 **{monster['name']}** (HP: {monster['hp']} | 공격력: {monster['atk']})"
        )

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("⚔️ 공격하기"):
                # 플레이어 공격
                player_damage = random.randint(15, 30) + (
                    st.session_state.level * 2
                )
                monster["hp"] -= player_damage
                add_log(
                    f"{monster['name']}에게 {player_damage}의 데미지를 입혔습니다!"
                )

                # 몬스터 처치 확인
                if monster["hp"] <= 0:
                    st.session_state.gold += monster["gold"]
                    st.session_state.exp += monster["exp"]
                    add_log(
                        f"🎉 {monster['name']}(을)를 처치했습니다! (+{monster['gold']} Gold, +{monster['exp']} EXP)"
                    )
                    st.session_state.monster = None

                    # 레벨업 체크
                    req_exp = st.session_state.level * 50
                    if st.session_state.exp >= req_exp:
                        st.session_state.level += 1
                        st.session_state.max_hp += 20
                        st.session_state.hp = st.session_state.max_hp
                        add_log(
                            f"🎊 레벨 업! Lv.{st.session_state.level}이 되었습니다! (최대 체력 증가)"
                        )

                    st.rerun()

                # 몬스터 반격
                monster_damage = random.randint(5, monster["atk"])
                st.session_state.hp -= monster_damage
                add_log(
                    f"{monster['name']}(이)가 반격하여 {monster_damage}의 피해를 입었습니다."
                )
                st.rerun()

        with col_b:
            if st.button("🏃 마을로 도망치기"):
                st.session_state.scene = "town"
                st.session_state.monster = None
                add_log("마을로 안전하게 도망쳤습니다.")
                st.rerun()

# ---------------------------------------------------------
# 4. 하단 모험 일지 (로그)
# ---------------------------------------------------------
st.divider()
st.subheader("📜 모험 일지")
for log_item in reversed(st.session_state.logs[-6:]):
    st.caption(f"- {log_item}")
