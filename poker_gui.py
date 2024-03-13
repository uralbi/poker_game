import time
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QFileDialog, QWidget, QMainWindow, QGraphicsDropShadowEffect
from PyQt5 import QtCore, QtWidgets
from utils import Deck, Hand, Balance, CompDec
from PyQt5.QtCore import QThread


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        try:
            loadUi("poker.ui", self)
        except Exception as e:
            file = os.path.join(os.path.dirname(sys.executable), 'poker.ui')
            loadUi(file, self)

        self.deck_types = ('images/deck1/', 'images/deck2/')
        self.backs = ('back.png', 'back2.png')
        self.deck_des = 1
        self.card_ratio = 3.6  # 4.6 for deck1 / 3.6 for deck2
        if self.deck_des == 0:
            self.card_ratio = 4.6
        self.card_spots = {self.comp_card1: '', self.comp_card2: '', self.card1: '', self.card2:'',
                           self.card3: '', self.card4: '', self.card5: '',
                           self.my_card1: '', self.my_card2: ''}
        self.deck = ''
        self.pot = 0
        self.comm_cards = []
        self.starter = 0 # who will start (0 comp, 1 player)
        self.bet_position = ('closed', 'p0', 0)
        self.current_stage = 0
        self.btns_state = 0

        self.player = QMediaPlayer()
        self.btn_start.clicked.connect(self.start_game)
        self.v_slider.valueChanged.connect(self.update_raise_label)

        self.hand_progress.setRange(0,100)
        self.hand_progress.setValue(0)

        self.btn_call.clicked.connect(lambda: self.my_response('call'))
        self.btn_bet.clicked.connect(lambda: self.my_response('bet'))
        self.btn_fold.clicked.connect(lambda: self.my_response('fold'))

        self.btn_change_cards.clicked.connect(self.change_cards)

    def update_raise_label(self):
        amount = self.v_slider.value()
        amnt = round(amount/100, 0)*100
        self.label_3.setText(f'{amnt}')

    def set_slider(self):
        self.v_slider.setSingleStep(100)
        self.v_slider.setMinimum(0)
        if p1.balance <= p2.balance:
            self.v_slider.setMaximum(int(p1.balance))
        else:
            self.v_slider.setMaximum(int(p2.balance))
        self.v_slider.setValue(0)

    def start_game(self):
        global p2, p1
        p1 = Hand()
        p2 = Hand()
        bal = 10000
        p2.set_balance(bal*3)
        p1.set_balance(bal)
        self.btn_open_my.clicked.connect(self.open_mycards)
        self.start_round()
        self.set_dealer()

    def start_round(self):
        self.btns_state = 1
        self.label_12_1.setStyleSheet("background:#404040; border-radius: 4px")
        self.unshadow(self.label_16)
        card_table = (self.card1, self.card2, self.card3, self.card4, self.card5, self.comp_card1, self.comp_card2,
                      self.my_card1, self.my_card2)
        for c in card_table:
            self.unshadow(c)
            c.clear()

        for l in self.card_spots.keys():
            l.setStyleSheet("border: none; border-radius: 10px;")

        self.comm_cards = []
        self.current_stage = 0
        self.deck = Deck()
        self.pot = 0
        self.bet_position=('closed', 'p0', 0)

        p1.clear()
        p2.clear()
        p1.add(self.deck.deal(2))
        p2.add(self.deck.deal(2))

        self.my_cards_show()
        self.comp_cards(False)
        self.set_slider()
        self.update_labels()

        self.init_bet(100)

        self.set_slider()

        self.update_computer_label('Starting the Round !')
        self.update_computer_label2('Your turn !')
        try:
            self.btn_continue.disconnect()
        except:
            pass

    def betting(self, player, amount=100):
        if self.bet_position[0] == 'closed':
            if player == 'p1':
                p1.pay(amount)
                self.label_13.setText(f'-{amount}')
                self.pot += amount
            else:
                p2.pay(amount)
                self.label_14.setText(f'-{amount}')
                self.pot += amount
            self.bet_position = ('open', player, amount)
        elif self.bet_position[1] != player:
            if player == 'p1':
                amount = self.bet_position[2]
                p1.pay(amount)
                self.label_13.setText(f'-{amount}')
                self.pot += amount
            else:
                p2.pay(amount)
                self.label_14.setText(f'-{amount}')
                self.pot += amount
        self.update_labels()
        self.set_slider()

    def folding(self, player):
        pot = self.pot
        if player == 'p1':
            p2.receive(pot)
        else:
            p1.receive(pot)
        self.btn_continue.clicked.connect(self.start_round)
        self.start_round()

    def calling(self, player):
        if player != self.bet_position[1]: # call
            amount = self.bet_position[2]
            if player == 'p1':
                p1.pay(amount)
                self.label_13.setText(f'-{amount}')
                self.pot += amount
            else:
                p2.pay(amount)
                self.label_14.setText(f'-{amount}')
                self.pot += amount

            if self.bet_position[0] == 'open':
                self.bet_position = ('closed', 'p0', 0)
                self.go_next_stage()
            else:
                self.bet_position = ('open', 'p0', 0)
            self.update_labels()
            self.set_slider()

    def comp_action(self):
        p2.analyse()
        p1act = self.bet_position[2]
        dec = 'call'
        if p1act == p2.balance or p1.balance == 0:
            self.update_computer_label('ALL IN!')
            self.update_computer_label2('')
            self.calling('p2')
            while self.current_stage < 3:
                self.go_next_stage()
            self.calling('p1')

        if dec == 'call':
            if p1act == 0:
                self.update_computer_label('I check!')
                self.update_computer_label2(' YOU TURN ')
                self.calling('p2')
            if p1act > 0:
                self.update_computer_label('I Call!')
                self.update_computer_label2(' YOU TURN ')
                self.calling('p2')

    def go_next_stage(self):
        name_scr = {'royal': 'Royal Flush', 'four': 'Four of a Kind', 'full_house': 'Full House',
                    'flush': 'Flush', 'straight': 'Straight', 'three': 'Three of a Kind',
                    'two_pairs': 'Two Pairs', 'one_pair': 'One Pair', 'high_card': 'High Card'}
        stage = self.current_stage
        if stage == 0:
            self.comm_cards = self.deck.deal(3)
            p1.add(self.comm_cards)
            p2.add(self.comm_cards)
            self.hand_progress.setValue(int(p1.hand_strenght()))
            self.open_flop()
            self.current_stage = 1
        elif stage == 1:
            turn_card = self.deck.deal(1)
            p1.add(turn_card)
            p2.add(turn_card)
            self.hand_progress.setValue(int(p1.hand_strenght()))
            self.open_turn(turn_card)
            self.current_stage = 2
        elif stage == 2:
            river_card = self.deck.deal(1)
            p1.add(river_card)
            p2.add(river_card)
            self.hand_progress.setValue(int(p1.hand_strenght()))
            self.open_river(river_card)
            self.current_stage = 3
        elif stage == 3:
            self.comp_cards(True)
            winner = self.finalizing()
            self.btns_state = 0
            if winner == 'p1':
                p1.receive(self.pot)
                self.label_14.setText(' ')
                self.label_13.setText(f'+{self.pot}')
            elif winner == 'p2':
                p2.receive(self.pot)
                self.label_14.setText(f'+{self.pot}')
                self.label_13.setText(' ')
            else:
                p1.receive(self.pot/2)
                p2.receive(self.pot/2)
                self.label_14.setText(f'+{self.pot/2}')
                self.label_13.setText(f'+{self.pot/2}')
            self.pot = 0

            self.label.setText(f'Winner is {winner}')

            self.update_labels()
            self.btns_state = 0
            self.btn_continue.clicked.connect(self.start_round)
            self.label_12.setStyleSheet("background:#404040; border-radius: 8px;")
            self.label_12_1.setStyleSheet("background:#391313; border-radius: 4px;")

            p1_pair = p1.playing_cards(p1.cards)[0]
            p2_pair = p2.playing_cards(p2.cards)[0]

            if winner == 'p1':
                self.label.setText(f'Winner is {winner}')
                self.update_computer_label(f'!!! YOU WON !!!')
                self.update_computer_label2(f'with the {name_scr[p1_pair]}')
            elif winner == 'p2':
                self.label.setText(f'Winner is {winner}')
                self.update_computer_label(f'!!! YOU LOST !!!')
                self.update_computer_label2(f'I won with the {name_scr[p2_pair]}')
            else:
                self.update_computer_label(f' * * * DRAW * * *')
                self.update_computer_label2(f'Lucky you!')

            if winner == 'p1':
                win_cards = p1.playing_cards(p1.cards)[1]
            elif winner == 'p2':
                win_cards = p2.playing_cards(p2.cards)[1]
            else:
                win_cards = []

            if win_cards:
                win_labels = []
                for k, v in self.card_spots.items():
                    if v in win_cards:
                        win_labels.append(k)
                for l in win_labels:
                    self.set_shadow(l)
                    l.setStyleSheet("border-bottom: 1px solid #ff9933; border-radius: 5px;"
                                    "border-top: 1px solid #ff9933;")
            self.set_shadow(self.label_16)

    def finalizing(self):
        base_scr = {'royal': 90, 'four': 80, 'full_house': 70, 'flush': 60, 'straight': 50,
                    'three': 40, 'two_pairs': 30, 'one_pair': 20, 'high_card': 0}

        p1_pair, p1_cards, p1_score = p1.playing_cards(p1.cards)
        p2_pair, p2_cards, p2_score = p2.playing_cards(p2.cards)
        winner = None
        if p1_pair == p2_pair:
            if p1_score > p2_score:
                winner = 'p1'
            elif p1_score < p2_score:
                winner = 'p2'

            else:
                winner = 'draw'

        elif base_scr[p1_pair] > base_scr[p2_pair]:
            winner = 'p1'
        else:
            winner = 'p2'

        self.label.setText(f'Winner is {winner}')

        return winner

    def my_response(self, resp):
        if self.btns_state:
            # resp: call bet fold
            if resp == 'call':
                self.calling('p1')
                self.comp_action()
            elif resp == 'bet':
                slider_val = int(round(self.v_slider.value() / 100, 0) * 100)
                if slider_val > 0:
                    self.betting('p1', slider_val)
                else:
                    self.betting('p1')
                self.comp_action()
            elif resp == 'fold':
                self.folding('p1')

    def init_bet(self, bet):
        self.label_14.setText(f'-{bet}') #COMP BET LABEL
        self.label_13.setText(f'-{bet}') #PLAYER BET LABEL
        self.pot += bet*2
        p1.pay(100)
        p2.pay(100)
        self.update_labels()
        self.label_12.setStyleSheet("background:#391313; border-radius: 8px;")

    def update_computer_label(self, info):
        self.label.setText(info)
        # self.label.adjustSize()

    def update_computer_label2(self, info):
        self.label_11.setText(info)
        # self.label_11.adjustSize()

    def open_flop(self):
        flop_table = (self.card1, self.card2, self.card3)
        flop_cards = self.comm_cards
        for c, i in zip(flop_table, flop_cards):
            self.card_spots[c] = i
            pixmap = QPixmap(f'{self.deck_types[self.deck_des]}{i}')
            pixmap.setDevicePixelRatio(self.card_ratio)
            c.setPixmap(pixmap)

    def my_cards_show(self):
        my_table = (self.my_card1, self.my_card2)
        for c, i in zip(my_table, p1.cards):
            self.card_spots[c] = i
            pixmap = QPixmap(f'bg/{self.backs[self.deck_des]}')
            pixmap.setDevicePixelRatio(self.card_ratio)
            c.setPixmap(pixmap)
        if self.cb_autoshow.isChecked():
            self.open_mycards()

    def comp_cards(self, is_show):
        ratio = self.card_ratio + 2.8
        if not is_show:
            my_table = (self.comp_card1, self.comp_card2)
            for c, i in zip(my_table, p2.cards):
                back_img = f'{self.backs[self.deck_des]}'
                pixmap = QPixmap(f'bg/{back_img}')
                pixmap.setDevicePixelRatio(ratio)
                c.setPixmap(pixmap)
        else:
            my_table = (self.comp_card1, self.comp_card2)
            for c, i in zip(my_table, p2.cards):
                self.card_spots[c] = i
                pixmap = QPixmap(f'{self.deck_types[self.deck_des]}/{i}')
                pixmap.setDevicePixelRatio(ratio)
                c.setPixmap(pixmap)

    def open_mycards(self):
        my_table = (self.my_card1, self.my_card2)
        for c, i in zip(my_table, p1.cards):
            pixmap = QPixmap(f'{self.deck_types[self.deck_des]}/{i}')
            pixmap.setDevicePixelRatio(self.card_ratio)
            c.setPixmap(pixmap)

    def back_card(self, card):
        bg_pixmap = QPixmap(f'bg/{self.backs[self.deck_des]}')
        bg_pixmap.setDevicePixelRatio(self.card_ratio)
        card.setPixmap(bg_pixmap)

    def open_turn(self, card):
        pixmap = QPixmap(f'{self.deck_types[self.deck_des]}{card[0]}')
        pixmap.setDevicePixelRatio(self.card_ratio)
        self.card4.setPixmap(pixmap)
        self.card_spots[self.card4] = card[0]

    def open_river(self, card):
        pixmap = QPixmap(f'{self.deck_types[self.deck_des]}{card[0]}')
        pixmap.setDevicePixelRatio(self.card_ratio)
        self.card5.setPixmap(pixmap)
        self.card_spots[self.card5] = card[0]

    def set_dealer(self):
        pixmap = QPixmap(f'images/ai3.webp')
        pixmap.setDevicePixelRatio(17)
        self.label_16.setPixmap(pixmap)


    def update_labels(self):
        """
        :return: update Pot, Balances
        """
        self.label_10.setText(f'{p2.balance}')
        self.label_6.setText(f'{p1.balance}')
        self.label_7.setText(f'{self.pot}')
        self.hand_progress.setValue(int(p1.hand_strenght()))

    def play_sound(self, file_path):
        full_file_path = os.path.join(os.getcwd(), f'sounds/{file_path}')
        url = QUrl.fromLocalFile(full_file_path)
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.play()

    # threading
    def start_worker_1(self):
        tr1 = ThreadClass(parent=None, index=1, info = 'some threading text')
        tr1.start()
        tr1.any_signal.connect(self.thr_label)
        tr1.sleep(3)
        tr1.stop()

    # threading
    def thr_label(self, info):
        self.label.setText(f'{info}')

    def change_cards(self):
        self.deck_des = 0 if self.deck_des else 1
        self.card_ratio = 3.6 if self.deck_des else 4.6
        # 4.6 for deck1 / 3.6 for deck2

    def set_shadow(self, obj):
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(255, 194, 102)) #color, satur, brightness, alpha channel
        shadow.setOffset(1)
        shadow.setBlurRadius(50)
        obj.setGraphicsEffect(shadow)

    def unshadow(self, obj):
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(0, 0, 0, 0)) #color, satur, brightness, alpha channel
        shadow.setOffset(0)
        shadow.setBlurRadius(20)
        obj.setGraphicsEffect(shadow)


class ThreadClass(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, index=0, info = ''):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True
        self.info = info

    def run(self):
        print('starting thread ..', self.index)
        # info = f'Threading info: {self.info}'
        self.any_signal.emit(self.info)

    def stop(self):
        self.is_running=False
        self.terminate()
        print('stopping thread')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    File = QtCore.QFile("/Users/uralbi/PycharmProjects/PyQT/qss/Combinear/Combinear.qss")
    # File = QtCore.QFile("/Users/uralbi/PycharmProjects/PyQT/qss/Neomorphism_w/neom.qss")
    if not File.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
        pass
    qss = QtCore.QTextStream(File)
    app.setStyleSheet(qss.readAll())

    ui = Ui_MainWindow()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(ui)
    widget.setMinimumWidth(1140)
    widget.setMinimumHeight(720)
    widget.setMaximumWidth(1140)
    widget.setMaximumHeight(720)
    widget.show()
    sys.exit(app.exec_())


