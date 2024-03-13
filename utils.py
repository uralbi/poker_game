import random
from collections import Counter


class Deck():
    def __init__(self):
        ccc = ['a', 'k', 'q', 'j', '10', '9', '8', '7', '6', '5', '4', '3', '2']
        bb = ['s', 'c', 'h', 'd']
        deck = [f'{i}{j}' for i in ccc for j in bb]
        random.shuffle(deck)
        self.deck = deck

    def __str__(self):
        return f'Deck with {len(self.deck)} cards'

    def deal(self, n_cards):
        """
        :param n_cards: number of cards to get
        :return: tuple of cards
        """
        cards = tuple(self.deck.pop() for i in range(n_cards))
        return cards

    def deal_me_kind(self, n_cards):
        cards = []
        for k in range(n_cards):
            for inx, i in enumerate(self.deck):
                if len(cards) > 0:
                    if cards[0][:-1] == i[:-1]:
                        cards.append(self.deck.pop(inx))
                        break
                else:
                    cards.append(self.deck.pop(inx))
                    break
        return cards

    def deal_me_flush(self, n_cards):
        cards = []
        for k in range(n_cards):
            for inx, i in enumerate(self.deck):
                if len(cards) > 0:
                    if cards[0][-1:] == i[-1:]:
                        cards.append(self.deck.pop(inx))
                        break
                else:
                    cards.append(self.deck.pop(inx))
                    break
        return cards


class Balance:
    def __init__(self):
        self.balance = 0

    def __str__(self):
        return f'Balance: {self.balance}'

    def set_balance(self, bal):
        self.balance = bal

    def pay(self, amount):
        self.balance -= amount
        return amount

    def receive(self, amount):
        self.balance += amount
        return amount


class CompDec:
    def __init__(self):
        self.comm_cards = []
        self.data = []
        self.strength = 0
        self.stage_decs = {}
        self.balance = 0
        self.p1_balance = 0

    def bets_history(self):
        # round_data = {}
        #   1) Qnty x: stages y: how many bets
        #   2) Amnt x: bet sequence, y : bet amounts
        #   3) Hand x: stages y: hands

        # hand correlation
        # risk aversion
        # bluffing
        return ('corr', 'avers', 'bluff')

    def clear(self):
        self.comm_cards.clear()
        self.bets.clear()
        self.stage = 0
        self.strength = 0
        self.stage_decs = {}

    def update_balance(self, self_amount, p1_amount):
        self.balance = self_amount
        self.p1_balance = p1_amount

    def get_data(self, stage, p1_dec, bet):
        # stage - p1_dec - bet
        self.data.append([stage, p1_dec, bet])

    def analyse2(self):
        bets = {}
        for i in self.data:
            bets[i[0]] = [i[1], i[2]]
        for k, v in bets.items():
            print(k, v)
            print('len of v', v)

    def decide(self):
        decision = 'call'
        amount = random.choice([100 * i for i in range(2, 9)])
        stgth = self.strength
        if amount > 600:
            decision = 'bet'
        return decision, amount


class Hand(CompDec, Balance):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.value = 0
        self.cc =['a', 'k', 'q', 'j', '10', '9', '8', '7', '6', '5', '4', '3', '2']

    def __str__(self):
        return f"{self.value} : {self.cards}"

    def analyse(self):
        my_cards = self.cards[:2]
        comm_cards = self.cards[2:]
        comm_strength = self.playing_cards(comm_cards)
        # print('comm_strength is', comm_strength)

    def clear(self):
        self.cards = []

    def add(self, cards):
        self.cards.extend([*cards])
        # self.value = self.playing_cards(self.cards)

    def check_flush(self, cards):
        level = None
        score = 0
        card_t = tuple(i[-1:] for i in cards)
        ct_pairs = Counter(card_t)  # count of card types
        flush_count = ['', 0]
        for k, v in ct_pairs.items():
            if v > flush_count[1]:
                flush_count = [k, v]
        if int(flush_count[1]) >= 5:
            level = 'flush'
            fl_cards = [c for c in cards if c[-1] == flush_count[0]]
            fl_cards = self.restack_cards(fl_cards)
            ms = 0
            for ix, c in enumerate(fl_cards):
                ms += self.max_card_calc(c)*(100**(4-ix))
            score = ms
            return level, fl_cards, score
        return level, flush_count

    def check_straight(self, cards):
        st_temp_cards = [*cards]
        if len(st_temp_cards) < 7:
            for i in range(7-len(st_temp_cards)):
                st_temp_cards.append('00')

        level = False
        score = 0
        card_remap = {14:'a', 13:'k', 12:'q', 11:'j'}
        get_card_v = [self.max_card_calc([c[:-1],0]) for c in st_temp_cards]
        get_card_v.sort(reverse=True)
        straight_str = ''
        sti = get_card_v[0]
        for i in get_card_v[1:]:
            res = f'{sti - i}'
            if res == '1':
                straight_str += res
            else:
                straight_str += '0'
            sti = i
        if '1111' in straight_str:
            dups = []
            dup_cards = []
            get_dups = Counter(get_card_v)
            for k,v in get_dups.items():
                if v >= 2:
                    dups.append(k)
            if dups:
                if len(dups) == 1:
                    dup_cards = [c for c in cards if c[:-1] == card_remap.get(dups[0], str(dups[0]))]
                else:
                    dup_cards1 = [c for c in cards if c[:-1] == card_remap.get(dups[0], str(dups[0]))]
                    dup_cards2 = [c for c in cards if c[:-1] == card_remap.get(dups[1], str(dups[1]))]
                    dup_cards = [dup_cards1,dup_cards2]
            fl_count = Counter([c[-1] for c in cards])
            fl_cnt = 0
            fl_val = ''
            for k,v in fl_count.items():
                if v > fl_cnt:
                    fl_val = k
                    fl_cnt = v

            rem_cards = []
            if dups:
                if len(dups) == 1:
                    if fl_val in [c[-1] for c in dup_cards]:
                        rem_cards = [k for k in dup_cards if k[-1] != fl_val]
                    elif dup_cards:
                        rem_cards = dup_cards[0]
                else:
                    for dc in dup_cards:
                        if fl_val in [c[-1] for c in dc]:
                            for c in dc:
                                if fl_val not in c:
                                    rem_cards.append(c)
                        else:
                            rem_cards.append(dc[0])
            if straight_str[:2] == '00' or straight_str[:2] == '10':
                straight_str = '0011111'
            elif straight_str[-2:] == '00' or straight_str[-2:] == '01':
                straight_str = '1111100'
            elif straight_str[0] == '0' and straight_str[-1] == '0':
                straight_str = '0111110'
            straight_list = list(straight_str)
            level = 'straight'
            str_cards = [c for (c,b) in zip(get_card_v, straight_list) if b=='1']
            str_cards = [card_remap.get(i, i) for i in str_cards]
            str_cards2=[]
            for k in str_cards:
                for c in cards:
                    if str(k) in c:
                        str_cards2.append(c)
            str_cards2 = [i for i in str_cards2 if i not in rem_cards]
            score = 400 + self.max_card_calc(str_cards2[0])
        else:
            str_cards2 = []
        return level, str_cards2[:5], score

    def max_card_calc(self, card):
        """
        :param card: list ['k', int]
        :return: int
        """
        sc_map = {'a': 14, 'k': 13, 'q': 12, 'j': 11, '0': 0}

        if type(card) == str:
            if card[0].isdigit():
                n1 = int(card[:-1])
                max_card = n1
            else:
                n1 = card[0]
                max_card = sc_map.get(n1, 0)
        else:
            if card[0].isdigit():
                n1 = int(card[0])
                max_card = n1
            else:
                n1 = card[0]
                max_card = sc_map.get(n1, 0)
        return max_card

    def get_best_pairs(self, cards):
        pair_level = ''
        card_v = tuple(i[:-1] for i in cards)
        cv_pairs = Counter(card_v)  # count of card values
        pairs_count = [(k, v) for k, v in cv_pairs.items()]
        check_pairs = [i[1] for i in pairs_count]
        fh_cards = [*cv_pairs.most_common()]
        # print('\n cv pairs: ', cv_pairs)
        # print(fh_cards, '\n')
        if 4 in check_pairs:
            pair_level = 'four'
            p_card = [c for c in cards if c[:-1] == fh_cards[0][0]]
            rs_cards = fh_cards[1:]
            m_val = max(rs_cards, key=lambda x: self.max_card_calc(x))
            rs_card = [c for c in cards if c[:-1] == m_val[0]][0]
            score = 700 + self.max_card_calc(p_card[0])
            p_card.append(rs_card)
            res_cards = p_card
        elif 3 in check_pairs and check_pairs.count(3) == 2:
            x1 = self.max_card_calc(fh_cards[0])
            x2 = self.max_card_calc(fh_cards[1])
            if x1 > x2:
                p_card = [c for c in cards if c[:-1] == fh_cards[0][0]]
                p_card2 = [c for c in cards if c[:-1] == fh_cards[1][0]][:2]
            else:
                p_card = [c for c in cards if c[:-1] == fh_cards[1][0]]
                p_card2 = [c for c in cards if c[:-1] == fh_cards[0][0]][:2]
            pair_level = 'full_house'
            mx = self.max_card_calc(p_card[0])
            score = 600+mx
            p_card.extend(p_card2)
            res_cards = p_card
        elif 3 in check_pairs and 2 in check_pairs:
            pair_level = 'full_house'
            fh_cards = [*cv_pairs.most_common(3)]
            mx = self.max_card_calc(fh_cards[0])
            p_cards = [c for c in cards if c[:-1] == fh_cards[0][0]]
            if check_pairs.count(2) == 2:
                mx_card = max(*fh_cards[1:], key=lambda x: self.max_card_calc(x))
            else:
                mx_card = fh_cards[1]
            sub_cards = [c for c in cards if c[:-1] == mx_card[0]]
            p_cards.extend(sub_cards)
            res_cards = p_cards
            score = 600+mx
        elif 3 in check_pairs:
            pair_level = 'three'
            p_cards = fh_cards[0]
            hc_cards = self.restack_cards(fh_cards[1:])
            sc_crds = [p_cards, *hc_cards]
            hc_cards = hc_cards[:2]
            pm_cards = [c for c in cards if c[:-1] == p_cards[0]]
            sub_cards = [c for c in cards if c[:-1] in [k[0] for k in hc_cards]]
            sub_cards = self.restack_cards(sub_cards)
            pm_cards.extend(sub_cards)
            res_cards = pm_cards
            sc_crds2 = [i for i in sc_crds][:3]
            mxs = 0
            for ix, sc in enumerate(sc_crds2):
                mx = self.max_card_calc(sc)*(100**(2-ix))
                mxs += mx
            score = mxs
        elif 2 in check_pairs:
            two_c = check_pairs.count(2)
            if two_c == 3:
                pair_level = 'two_pairs'
                p_cards = sorted(fh_cards[:-1], key=lambda x: self.max_card_calc(x), reverse=True)
                mxs = 0
                for ix, k in enumerate(p_cards):
                    mxs += self.max_card_calc(k) * (100 ** (2 - ix))
                res_cards = [c for c in cards if c[:-1] in [k[0] for k in p_cards[:2]]]
                rs_card = [c for c in cards if c[:-1] == p_cards[-1][0]][0]
                res_cards.append(rs_card)
                res_cards = sorted(res_cards, key= lambda x: self.max_card_calc(x), reverse=True)
                score = mxs
            elif two_c == 2:
                pair_level = 'two_pairs'
                p_cards = fh_cards[:2]
                p_cards = sorted(p_cards, key= lambda x: self.max_card_calc(x), reverse=True)
                res_cards = [c for c in cards if c[:-1] in [k[0] for k in p_cards]]
                res_cards = self.restack_cards(res_cards)
                rs_cards = fh_cards[2:]
                if len(rs_cards) > 1:
                    m_card = max(rs_cards, key=lambda x: self.max_card_calc(x))
                    m_card2 = [c for c in cards if c[:-1] == m_card[0]]
                    p_cards.append((m_card))
                else:
                    # print(fh_cards)
                    rs_card = list(fh_cards[2:][0])
                    m_card2 = [c for c in cards if c[:-1] == f'{rs_card[0]}']
                    m_card = self.max_card_calc(rs_card)
                    p_cards.append((f'{m_card}',0))
                res_cards.append(*m_card2)
                mxs = 0
                for ix, k in enumerate(p_cards):
                    mxs += self.max_card_calc(k)*(100**(2-ix))
                score = mxs
            else:
                pair_level = 'one_pair'
                p_cards = fh_cards[0]
                hc_cards = self.restack_cards(fh_cards[1:])
                hc_cards = sorted(hc_cards, key=lambda x: self.max_card_calc(x), reverse=True)[:3]
                res_cards = [c for c in cards if c[:-1] == p_cards[0]]
                res_cards2 = [c for c in cards if c[:-1] in [k[0] for k in hc_cards]]
                res_cards2 = sorted(res_cards2, key=lambda x: self.max_card_calc(x), reverse=True)
                res_cards.extend(res_cards2)
                mxs=0
                for idx, hc in enumerate(hc_cards):
                    mxs+= self.max_card_calc(hc)*(1000**(2-idx))
                score = (10**8)*self.max_card_calc(p_cards) + mxs
        else:
            p_cards = sorted(fh_cards, key=lambda x: self.max_card_calc(x), reverse=True)[:5]
            res_cards = [c for c in cards if c[:-1] in [k[0] for k in p_cards]]
            res_cards = self.restack_cards(res_cards)
            mxs = 0
            for idx, hc in enumerate(p_cards):
                mxs += self.max_card_calc(hc) * (100 ** (4 - idx))
            score = mxs
            pair_level = 'high_card'
        return pair_level, res_cards, score

    def playing_cards(self, cards):
        # royal, four, full_house, flush, straight, three, two_pairs, one_pair, high_card
        # 1 four 700
        #   --> fullhouse 600
        #       --> flush + straight (royal) 900
        #           --> flush (500) or straight(400)
        #               --> three onely (300)
        #                   --> two pairs (200)
        #                       --> one pair (100)
        #                           --> high card (0)
        allcards = cards
        _pairs = self.get_best_pairs(allcards)
        if _pairs[0] == 'full_house':
            return _pairs
        elif self.check_flush(allcards)[0]:
            flv = self.check_flush(allcards)
            straight_res = self.check_straight(flv[1])

            if not straight_res[0]:
                return flv[0], flv[1][:5], flv[2]
            else:
                level = 'royal'
                royal = straight_res[1]
                score = 900 + self.max_card_calc(royal[0])

                return level, royal, score
        elif self.check_straight(allcards)[0]:
            str_hand = self.check_straight(allcards)
            return str_hand
        else:
            return _pairs

    def restack_cards(self, cards):
        res_cards = []
        for i in self.cc:
            for c in cards:
                if i in c:
                    res_cards.append(c)
        return res_cards

    def hand_strenght(self):
        # royal, four, full_house, flush, straight, three, two_pairs, one_pair, high_card
        base_scr = {'royal':90, 'four':80, 'full_house':70, 'flush':60, 'straight':50,
                    'three':40, 'two_pairs':30, 'one_pair':20, 'high_card': 0}
        str_ = 0
        if self.cards:
            hand = self.playing_cards(self.cards)
            level = hand[0]
            max_card = hand[1][0]
            str_ = base_scr.get(level, 0) + round(self.max_card_calc(max_card)*0.71, 1)
        return str_


if __name__ == "__main__":
    pass




