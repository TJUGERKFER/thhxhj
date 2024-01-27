# DEV BY TJUGERKFER
import random
from typing import Any
import pygame
import json

from pygame.math import Vector2
import asset
import time
import gzip
import os

pygame.init()
pygame.mixer.set_num_channels(40)
pygame.display.set_caption('STGGAME')
V2 = pygame.math.Vector2
# posvec：位置向量 speedvec：速度向量


class playerCharacter(pygame.sprite.Sprite):  # 判定点类
    def __init__(self, radius, speed, speedMultiplier, QTElimit, attackspeed, temperature, tempdownspeed, spellcardname, drawsprite):
        super().__init__()
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.image.fill('BLUE')
        self.image.set_colorkey("BLUE")
        self.rect = self.image.get_rect()
        self.radius = radius
        pygame.draw.circle(self.image, 'WHITE',
                            (self.radius, self.radius), self.radius-3)
        self.mask = pygame.mask.from_surface(self.image) # 使得实际判定遮罩比判定点更小
        self.posvec = V2(455, 600)
        self.rect = self.image.get_rect()
        self.image.fill('BLUE')
        self.image.set_colorkey("BLUE")
        self.rect.centerx = 455
        self.rect.centery = 600
        self.nowattackspeed = self.attackSpeed = attackspeed
        self.attackCoolDown = 0
        self.speedvec = V2(0, 0)
        self.speed = speed
        self.slow = 1
        self.spellcardname = spellcardname
        self.drawsprite = drawsprite
        self.speedMultiplier = speedMultiplier
        self.shoot = False
        self.HP = 5
        self.Bomb = 3
        self.leftspeed = 0
        self.rightspeed = 0
        self.upspeed = 0
        self.downspeed = 0
        self.invincibleTime = 0
        self.QTETime = 0
        self.QTElimit = QTElimit
        self.status = "alive"
        self.mode = 1
        self.missinthisspell = False
        self.graze = 0
        self.temperature = temperature
        self.keeptemptime = 60
        self.tempdownspeed = tempdownspeed
        self.liferecprog = 0
        self.liferectotal = 100000 # 初始恢复槽上限为100000
    def setmode(self, mode):  # 设置子机位置
        if mode == 1:
            self.slow = self.speedMultiplier
            pygame.draw.circle(self.image, 'WHITE',
                               (self.radius, self.radius), self.radius)
            pygame.draw.circle(self.image, 'RED',
                               (self.radius, self.radius), self.radius, 1)
            player_CharacterOptionRight.x = 16
            player_CharacterOptionRight.y = -23
            player_CharacterOptionLeft.x = -16
            player_CharacterOptionLeft.y = -23
        if mode == 0:
            self.slow = 1
            self.image.fill('BLUE')
            self.image.set_colorkey("BLUE")
            player_CharacterOptionRight.x = 27
            player_CharacterOptionRight.y = 28
            player_CharacterOptionLeft.x = -27
            player_CharacterOptionLeft.y = 28
        self.mode = mode

    def update(self, choosecharacter):
        global score
        assert (self.keeptemptime >= 0)
        if self.keeptemptime == 0:  # 保温时间已过
            self.temperature = max(
                self.temperature - self.tempdownspeed, 0)  # 温度限制
        else:
            self.keeptemptime -= 1
        if self.temperature > 80000: # 溢出温度转化为生命恢复槽进度和分数
            self.liferecprog += (self.temperature - 80000)
            score += (self.temperature - 80000)
            self.temperature = 80000
        if self.liferecprog > self.liferectotal: # 攒满生命恢复槽
            self.liferecprog = 0
            self.liferectotal += 20000 # 增加难度
            se.play("extend",se.SPELL_EXTEND_CHANNEL)
            if self.HP < 9:
                self.HP += 1 
            else: 
                self.Bomb += 1
        if choosecharacter == "Marisa":
            for item in bombgroup:
                item.angle += 3
                if item.angle > 360:
                    item.angle = 0
        self.speedvec.x = self.rightspeed - self.leftspeed
        self.speedvec.y = self.downspeed - self.upspeed
        if self.speedvec.length():
            self.speedvec.scale_to_length(
                self.speed * self.slow)  # 算出速度方向并乘以速度标量
            self.posvec += self.speedvec
            self.posvec.x = min(gameZoneRight - self.rect.width, self.posvec.x)
            self.posvec.x = max(40, self.posvec.x)
            self.posvec.y = min(gameZoneDown - self.rect.height, self.posvec.y)
            self.posvec.y = max(50, self.posvec.y)
            self.rect.centerx, self.rect.centery = self.posvec
        # 伪状态机
        if self.status == "alive":
            self.missCheck()
        if self.status == "dying":
            self.missCheck()
            self.QTECheck()
        if self.status == "invincible":
            self.missCheck()
            self.invincibleCheck()
        if self.status == "usebomb":
            self.Bomb -= 1
            se.play("bomb", se.PLAYER_SPELL_CHANNEL)
            effectgroup.add(CharacterDrawSprite(
                self.drawsprite, (self.drawsprite.get_width()/2, 900 + self.drawsprite.get_height()/2)))
            effectgroup.add(CharacterDrawSprite(gameui.font_24.render(
                self.spellcardname, True, "BLACK"), (self.drawsprite.get_width()/2, 900)))
            self.missinthisspell = True
            if self.QTETime:  # 决死
                self.QTETime = 0
            self.status = "bombing"
            if choosecharacter == "Reimu":
                # 下面这段是Bing AI优化的
                # 创建一个列表，包含不同颜色的图片对象
                pictures = [player_bomb_pictures[color] for color in [
                    "red", "orange", "yellow", "green", "blue", "purple"]]
                # 创建一个列表，包含不同的位置和参数
                positions = [(self.rect.centerx - 80, self.rect.centery - 150, 210),
                             (self.rect.centerx + 80, self.rect.centery - 150, 215),
                             (self.rect.centerx + 150, self.rect.centery, 220),
                             (self.rect.centerx + 80, self.rect.centery + 150, 225),
                             (self.rect.centerx - 80, self.rect.centery + 150, 230),
                             (self.rect.centerx - 150, self.rect.centery, 235)]
                # 遍历两个列表，创建和添加每个bomb对象
                for picture, position in zip(pictures, positions):
                    mybomb = ReimuBomb(picture, V2(
                        *position[:2]), V2(0, -0.1), position[2], 2)
                    bombgroup.add(mybomb)
            self.bombingTime = 180
        if self.status == "bombing":
            self.missCheck()
            self.bombingCheck()
        if self.shoot:
            if self.attackCoolDown - self.nowattackspeed:  # 射击冷却计算
                self.attackCoolDown += 1
                return
            self.attackCoolDown = 0  # 重置射击冷却并播放射击音效
            se.play("shoot")
            self.nowattackspeed = self.attackSpeed
            if choosecharacter == "Reimu":  # 为什么是全局变量 因为懒
                # 红白主机子弹
                selfBulletGroup.add(Bullet(self.spell_image, (255, 0, 0), 10, 30, V2(
                    self.rect.centerx + 8, self.rect.y - 5), V2(0, -40), 10, 0, False, V2(0, 0)))
                selfBulletGroup.add(Bullet(self.spell_image, (255, 0, 0), 10, 30, V2(
                    self.rect.centerx - 8, self.rect.y - 5), V2(0, -40), 10, 0, False, V2(0, 0)))
            elif choosecharacter == "Marisa":
                # 黑白主机子弹
                selfBulletGroup.add(Bullet(self.bulletimage, (255, 255, 128), 10, 300, V2(
                    self.rect.x + 13, self.rect.y - 10), V2(0, -30), 15, 0, False, V2(0, 0)))
                selfBulletGroup.add(Bullet(self.bulletimage, (255, 255, 128), 10, 300, V2(
                    self.rect.x - 7, self.rect.y - 10), V2(0, -30), 15, 0, False, V2(0, 0)))

    def bombingCheck(self):
        self.bombingTime -= 1
        if choosecharacter == "Marisa":
            color = random.choice(["red", "green", "yellow"])
            bombgroup.add(MarisaBomb(player_bomb_pictures[color][0], V2(
                self.rect.centerx, self.rect.centery - 40), V2(random.uniform(-1.5, 1.5), random.uniform(-3.5, -5.5)), 8, color))
        if not self.bombingTime:
            self.status = "alive"

    def QTECheck(self):
        self.QTETime -= 1
        if self.Bomb == 0:  # 没B直接寄
            self.QTETime = 0
        if not self.QTETime:
            self.status = "invincible"
            self.invincibleTime = 120
            self.HP -= 1
            self.temperature = max(self.temperature - 10000, self.temperature/2)
            self.missinthisspell = True
            self.clearradius = 10
            self.diecenter = self.rect.center
            self.Bomb = max(2, self.Bomb)
            pygame.draw.circle(self.image, 'WHITE', (5, 5), 5)
            pygame.draw.circle(self.image, 'RED', (5, 5), 5, 1)
            self.setmode(mode=self.mode)

    def invincibleCheck(self):
        self.invincibleTime -= 1
        if 0 < self.clearradius < 600:  # 创造出一个以死亡点为圆心的扩大消弹的圆
            self.clearradius += 25
            for item in enemyBulletGroup:
                if (item.rect.center[0]-self.rect.center[0])**2 + (item.rect.center[1]-self.rect.center[1])**2 < self.clearradius**2:
                    sprite_disappear(item, 8)
        else:
            self.clearradius = 0
        if not self.invincibleTime:
            self.status = "alive"

    def missCheck(self):
        self.iscoll = False
        for item in enemyBulletGroup:
            global score
            if pygame.sprite.collide_circle_ratio(2)(item, self) and not item.alreadyGraze:
                if self.status == "alive": # 防止东方擦擦乐
                    self.temperature += 1000  # 擦弹加温度
                player_Character.keeptemptime = 60  # 重置保温计数器
                self.graze += 1
                se.play("graze")
                effect = Bullet(2, (240, 240, 240), 8, 8, V2(self.rect.centerx, self.rect.centery), V2(
                    random.uniform(-1, 1), random.uniform(-1, 1)).normalize()*4, 0, 0, False, V2(0, 0))
                effectgroup.add(effect)
                sprite_disappear(effect, 20)
                score += 2000 if self.temperature <60000 else 2500
                item.alreadyGraze = True  # 擦过的弹不能再擦
            offset=(item.rect.x-self.rect.x,item.rect.y-self.rect.y)    #被减数和减数次序不能交换
            if self.mask.overlap(item.mask,offset): 
            #if pygame.sprite.collide_circle_ratio(0.5)(item, self):
                self.iscoll = item
                break
        if self.iscoll:
            item.kill()
            if self.status == "alive":  # 活着被弹转移到决死反应时间
                se.play("miss", se.MISS_CHANNEL)
                self.QTETime = 10
                self.status = "dying"
                pygame.draw.circle(self.image, 'RED', (5, 5), 5)


class playerCharacterImage(pygame.sprite.Sprite):  # 自机点阵图
    def __init__(self, imagec, imagel, imager):
        super().__init__()
        self.image = self.imagec = imagec
        self.imagel = imagel
        self.imager = imager
        self.leftspeed = 0
        self.rightspeed = 0

    def update(self):
        self.rect = self.image.get_rect()
        self.rect.center = player_Character.rect.center
        tmpspeed = self.rightspeed - self.leftspeed
        if not tmpspeed:  # 同时按左和右也为0
            self.image = self.imagec
            return
        if tmpspeed > 0:
            self.image = self.imager
            return
        self.image = self.imagel


class playerOption(pygame.sprite.Sprite):  # 子机类
    def __init__(self, image, x, y, attackSpeed, slowattackSpeed):
        super().__init__()
        self.originimage = self.image = image
        self.slowattackSpeed = slowattackSpeed
        self.attackSpeed = attackSpeed
        self.angle = 0
        self.shoot = False
        self.attackSpeed = attackSpeed
        self.slowattackSpeed = slowattackSpeed
        self.attackCoolDown = 0
        self.slow = False
        self.x = x
        self.y = y

    def update(self):
        self.attackCoolDown += 1
        self.rect = self.image.get_rect()
        width, height = self.image.get_size()
        self.rect.center = (player_Character.rect.centerx +
                            self.x, -height / 2 + player_Character.rect.centery + self.y)
        self.image = pygame.transform.rotate(self.originimage, self.angle+1)
        self.rect = self.image.get_rect(
            center=self.rect.center)  # 重新获取中心 避免转动问题
        self.angle += 1
        if self.angle > 360:
            self.angle = 0
        if self.shoot == False:  # 未射击直接返回
            return
        if player_Character.temperature < 10000:  # 温度小于10000禁止副机射击
            return
        if choosecharacter == "Reimu":
            if self.slow == False and self.attackSpeed < self.attackCoolDown:  # 红白诱导
                se.play("shoot")
                selfBulletGroup.add(Bullet(player_Character.spell_blue_image, (255, 255, 255), 10, 10, V2(
                    self.rect.centerx, self.rect.centery + 10), V2(0, -20), 6, 0, True, V2(0, 0))
                )
                self.attackCoolDown = 0
                return
            if self.slow == True and self.slowattackSpeed < self.attackCoolDown:  # 红白集中
                se.play("shoot")
                selfBulletGroup.add(Bullet(player_Character.spell_purple_image, (255, 0, 0), 10, 30, V2(
                    self.rect.centerx, self.rect.centery + 10), V2(0, -40), 10, 0, False, V2(0, 0)))
                self.attackCoolDown = 0
                return
        if choosecharacter == "Marisa":
            if self.slow == False and self.attackSpeed < self.attackCoolDown:  # 黑白激光
                selfBulletGroup.add(Bullet(0, (255, 255, 128), 10, 300, V2(self.rect.x + 13,
                                                                                            self.rect.y + 160), V2(0, -300), 1, self, False, V2(0, 0)))
                self.attackCoolDown = 0
                return
            elif self.slow == True and self.slowattackSpeed < self.attackCoolDown:  # 黑白导弹
                selfBulletGroup.add(Bullet(player_Character.missile_image, (255, 255, 128), 10, 300, V2(
                    self.rect.centerx, self.rect.y - 10), V2(0, -1), 18, 0, False, V2(0, -0.5)))
                self.attackCoolDown = 0
                return


class MoveData():  # 移动函数的结构体
    class MoveBetween():
        def __init__(self, speed, pointlist):
            self.speed = speed
            self.pointlist = pointlist.copy()
            self.name = "movebetween"
            self.movecounter = 0

    class SetSpeed():
        def __init__(self, speedvec):
            self.name = "setspeed"
            self.speedvec = speedvec

    class Sleep():
        def __init__(self, tick):
            self.name = "sleep"
            self.lasttick = self.tick = tick

    class MoveInTime():
        def __init__(self, tick, point):
            self.name = "moveintime"
            self.lasttick = self.tick = tick
            self.point = point


class SpriteMover():  # 精灵移动器
    def __init__(self, owner):
        self.owner = owner

    def reload(self, commandlist):
        self.commandlist = commandlist
        self.commandcounter = 0

    def update(self):
        if self.commandcounter == len(self.commandlist):  # 如果完成整个指令序列的所有指令
            self.commandcounter = 0
        if self.commandlist[self.commandcounter].name == "movebetween":
            self.movebetween()
            self.move()
            return
        if self.commandlist[self.commandcounter].name == "setspeed":
            self.setspeed()
            self.move()
            return
        if self.commandlist[self.commandcounter].name == "sleep":
            self.sleep()
            self.move()
            return
        if self.commandlist[self.commandcounter].name == "moveintime":
            self.moveintime()
            self.move()
            return

    def move(self):
        self.owner.posvec = self.owner.posvec + self.owner.speedvec
        self.owner.posvec.x = min(
            gameZoneRight - self.owner.rect.width, self.owner.posvec.x)
        self.owner.posvec.x = max(self.owner.rect.width, self.owner.posvec.x)
        self.owner.posvec.y = min(
            gameZoneDown - self.owner.rect.height, self.owner.posvec.y)
        self.owner.posvec.y = max(self.owner.rect.height, self.owner.posvec.y)
        self.owner.rect.centerx, self.owner.rect.centery = self.owner.posvec

    def movebetween(self):
        nowstep = self.commandlist[self.commandcounter]  # nowstep是目前执行到的脚本指令
        # 如果被移动精灵与目标点的位置小于每帧速度
        if (nowstep.pointlist[nowstep.movecounter] - self.owner.posvec).length() < nowstep.speed:
            # 直接移动到目标点
            self.owner.posvec = nowstep.pointlist[nowstep.movecounter]
            nowstep.movecounter += 1  # 指针指向下一个目标点
            if nowstep.movecounter == len(nowstep.pointlist):  # 如果已经完成整个列表中每个目标点
                nowstep.movecounter = 0  # 重置目标点指针
                self.commandcounter += 1  # 指针指向下一个脚本指令
            return
        # 从现在的位置向第movecounter位移动
        self.owner.speedvec = (
            nowstep.pointlist[nowstep.movecounter] - self.owner.posvec).normalize()*nowstep.speed

    def setspeed(self):
        nowstep = self.commandlist[self.commandcounter]
        self.owner.speedvec = V2(0, 0) + nowstep.speedvec
        self.commandcounter += 1

    def sleep(self):
        nowstep = self.commandlist[self.commandcounter]
        nowstep.lasttick -= 1
        if nowstep.lasttick == 0:
            nowstep.lasttick = nowstep.tick
            self.commandcounter += 1

    def moveintime(self):
        nowstep = self.commandlist[self.commandcounter]
        if nowstep.tick == nowstep.lasttick:
            self.owner.speedvec = (
                nowstep.point - self.owner.posvec) / nowstep.tick
        nowstep.lasttick -= 1
        if nowstep.lasttick == 0:
            self.commandcounter += 1
            self.owner.speedvec = V2(0, 0)
            nowstep.lasttick = nowstep.tick


class bulletitem(pygame.sprite.Sprite):  # 道具类
    def __init__(self, posvec: pygame.math.Vector2):
        super().__init__()
        self.image = gameui.bulletitem
        self.rect = self.image.get_rect()
        self.posvec = posvec

    def update(self):
        self.speedvec = relative_direction(
            self, player_Character).normalize()*20
        self.posvec = self.speedvec + self.posvec
        self.rect.center = self.posvec
        if pygame.sprite.collide_circle(self, player_Character):
            se.play("shoot")
            global score
            player_Character.temperature += 50  # 点数加温度
            self.kill()


class Bullet(pygame.sprite.Sprite):  # 子弹类
    def __init__(self, shape, color, width, height, posvec: pygame.math.Vector2, speedvec: pygame.math.Vector2, damage, free, track, accvec: pygame.math.Vector2):
        super().__init__()
        self.origincolor = self.color = color
        self.shape = shape
        self.accvec = accvec
        self.image = pygame.Surface([width, height])  # 控制子弹类型 但是目前看来这样写下去会更加屎山
        if shape == 2:
            pygame.draw.circle(self.image, color, (width/2, height/2), width/2)
            self.image.set_colorkey('BLACK')
        elif shape == 1:
            pygame.draw.circle(self.image, color, (width/2, height/2), width/2)
            pygame.draw.circle(
                self.image, (color[0]+14, color[1]+14, color[2]+14), (width/2, height/2), width/3)
            pygame.draw.circle(self.image, 'WHITE',
                               (width/2, height/2), width/2-2, 1)
            self.image.set_colorkey('BLACK')
        elif shape == 0:
            self.image.fill(color)
        else:
            self.originimage = self.image = self.shape
        self.rect = self.image.get_rect()
        self.posvec = posvec
        self.speedvec = speedvec
        self.inputspeedvec = speedvec
        self.rect.centerx, self.rect.centery = posvec
        self.damage = damage
        self.free = free  # 0产生跟随子机y轴移动的激光
        if self.free:
            self.image.set_alpha(128)
        self.track = track
        if track:
            self.lifetime = 0  # 为了实现诱导弹诱导效果逐渐加强
        self.width = width
        self.height = height
        self.alreadyGraze = False
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        self.posvec += self.speedvec
        self.speedvec += self.accvec
        self.rect.centerx, self.rect.centery = self.posvec  # 这行及上两行实现非整数坐标
        if self.track:  # 诱导弹
            self.lifetime += 1
            if self.lifetime <= 20: # 20帧的诱导过程
                self.speedvec = (self.lifetime*relative_direction(self, baka) + (20-self.lifetime)*self.inputspeedvec.normalize())
                self.speedvec.scale_to_length(self.inputspeedvec.length())
            else:
                self.speedvec = relative_direction(self, baka)
                self.speedvec.scale_to_length(
                    self.inputspeedvec.length())  # 速度向量转化为长度与输入速度一致
            self.image = pygame.transform.rotate(
                self.originimage, -V2(0, -1).angle_to(self.speedvec))
            self.rect = self.image.get_rect(
                center=self.rect.center)  # 重新获取中心 避免转动问题
        if self.rect.x - self.width > gameZoneRight + 50 or self.rect.x + self.width < gameZoneLeft - 50 or self.rect.y - self.rect.height > gameZoneDown + 50 or self.rect.y + self.height < gameZoneUp - 50:  # 出界判定
            self.kill()
        if self.free:
            self.rect.centerx = self.posvec.x = self.free.rect.centerx

    def tobulletitem(self):
        itemGroup.add(bulletitem(self.posvec))
        self.kill()


class MarisaBomb(pygame.sprite.Sprite):  # 抄袭自灵梦Bomb类型 别问我为什么不复用 问就是懒和不会
    def __init__(self, image, posvec: pygame.math.Vector2, speedvec: pygame.math.Vector2, damage, color):
        super().__init__()
        self.image = self.originimage = image
        self.rect = self.image.get_rect()
        self.posvec = posvec
        self.rect.centerx, self.rect.centery = posvec
        self.speedvec = speedvec
        self.damage = damage
        self.trigger = 0
        self.angle = 0
        self.lifetime = 180
        self.radius = 24
        self.color = color

    def update(self):
        self.lifetime -= 1
        if self.lifetime % 2 == 0:  # 尝试每两帧旋转一次降低开销
            self.angle += 3
            if self.angle > 360:
                self.angle = 0  # 使我的星星旋转
            self.image = player_bomb_pictures[self.color][int(self.angle/3)]
            self.rect = self.image.get_rect(center=self.rect.center)
        # self.posvec.x , self.posvec.y = self.rect.centerx , self.rect.centery 没这行有问题 有这行更有问题
        self.posvec += self.speedvec
        self.rect.centerx, self.rect.centery = self.posvec
        if not self.trigger:
            if pygame.sprite.collide_circle(self, baka):
                self.trigger = 1  # 击中则被触发
                if not baka.recovering:
                    baka.HP -= self.damage
            if not self.lifetime:
                self.trigger = 1
        if self.trigger and self.lifetime % 2 == 0:  # 逐渐变大消失
            self.image = pygame.transform.scale(self.image, (self.image.get_width(
            ) * (1 + 0.04 * self.trigger), self.image.get_height() * (1 + 0.04 * self.trigger)))
            self.trigger += 1
            self.image.set_alpha(255 - self.trigger * 15)
        if self.trigger > 20:
            self.kill()
        if not self.lifetime:  # 超过生命周期也消失
            self.kill()
        for item in enemyBulletGroup:
            if pygame.sprite.collide_circle(self, item):
                sprite_disappear(item, 5)


class ReimuBomb(pygame.sprite.Sprite):
    def __init__(self, image, posvec: pygame.math.Vector2, speedvec: pygame.math.Vector2, lifetime, damage):
        super().__init__()
        self.image = self.originimage = image
        self.rect = self.image.get_rect()
        self.posvec = posvec
        self.inputvec = self.speedvec = speedvec
        self.inputspeedvec = speedvec
        self.rect.centerx, self.rect.centery = posvec
        self.damage = damage
        self.inputlifetime = self.lifetime = lifetime
        self.tracktime = 200
        self.angle = 0
        self.trigger = False
        self.image.set_alpha(0)
        self.radius = 63

    def update(self):
        if 10 > self.lifetime - self.tracktime > 0:  # 10帧的逐渐出现效果
            self.image = self.originimage
            self.image.set_alpha(
                255 - (self.lifetime - self.tracktime) / 10 * 255)
        if self.tracktime > self.lifetime:
            self.angle += 3
            if self.angle > 360:
                self.angle = 0  # 使我的阴阳玉旋转
            self.image = pygame.transform.rotate(self.originimage, self.angle)
            if not self.trigger:
                self.speedvec = (self.speedvec + relative_direction(self, baka)*3).normalize() * (
                    self.inputspeedvec.length() + 0.08 * (self.tracktime - self.lifetime))
            else:
                self.speedvec = (self.speedvec + relative_direction(self, baka)*5).normalize() * (
                    self.inputspeedvec.length() + 0.08 * (self.tracktime - self.lifetime))
            self.rect = self.image.get_rect(center=self.rect.center)
            self.posvec.x, self.posvec.y = self.rect.centerx, self.rect.centery
            self.posvec += self.speedvec
            self.rect.centerx, self.rect.centery = self.posvec
        if pygame.sprite.collide_circle_ratio(0.8)(self, baka) and not baka.recovering:
            baka.HP -= self.damage
            if not self.trigger:
                self.trigger = 1  # 击中则被触发
        self.lifetime -= 1
        if self.trigger:  # 逐渐变大消失
            self.image = pygame.transform.scale(self.image, (self.image.get_width(
            ) * (1 + 0.03 * self.trigger), self.image.get_height() * (1 + 0.03 * self.trigger)))
            self.trigger += 1
            self.image.set_alpha(255 - self.trigger * 4)
        if self.trigger > 63:
            if not baka.recovering:
                baka.HP -= 50
                se.play("destory")
            self.kill()
        if not self.lifetime:  # 超过生命周期也消失
            self.kill()
        for item in enemyBulletGroup:
            if pygame.sprite.collide_circle(self, item):
                sprite_disappear(item, 5)


class LimitTimePic(pygame.sprite.Sprite):  # 图片精灵
    def __init__(self, image, posvec, lifetime=-1):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.posvec = posvec
        self.lifetime = self.lastlifetime = lifetime

    def setimage(self,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.posvec

    def update(self):
        if self.lifetime == -1:
            return
        self.lastlifetime -= 1
        if self.lastlifetime == 0:
            self.kill()


class PictureAppearEffect(pygame.sprite.Sprite):  
    def __init__(self, image,speed,originposvec:pygame.math.Vector2,reverse:bool,distance,initstatus = "appearing"):
        super().__init__()
        self.image = image.copy()
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.originposvec = originposvec
        self.rect.x, self.rect.y = originposvec
        self.status = "done"
        self.speed = speed
        self.reverse = reverse
        self.distance = distance
        if initstatus == "appearing":
            self.appear()
        if initstatus == "disappearing":
            self.disappear()
        if initstatus == "appeared":
            self.image.set_alpha(255)
        if initstatus == "disappeared":
            self.image.set_alpha(0)
    def appear(self):
        self.status = "appearing"
        if self.reverse:
            self.rect.x = self.originposvec.x + self.distance.x
            self.rect.y = self.originposvec.y + self.distance.y
        else:
            self.rect.x = self.originposvec.x - self.distance.x
            self.rect.y = self.originposvec.y - self.distance.y
                
    def disappear(self):
        self.status = "disappearing"

    def update(self):
        if self.status == "done":
            return
        if self.status == "appearing": # 致命屎山嵌套
            if self.reverse: 
                self.rect.x -= self.speed.x
                self.rect.y -= self.speed.y
                if self.rect.x <= self.originposvec.x:
                    self.rect.x = self.originposvec.x
                if self.rect.y <= self.originposvec.y:
                    self.rect.y = self.originposvec.y
                if (self.rect.x , self.rect.y) == self.originposvec:
                    self.status = "done"
            else:
                self.rect.x += self.speed.x
                self.rect.y += self.speed.y
                if self.rect.x >= self.originposvec.x:
                    self.rect.x = self.originposvec.x
                if self.rect.y >= self.originposvec.y:
                    self.rect.y = self.originposvec.y
                if (self.rect.x , self.rect.y) == self.originposvec:
                    self.status = "done"

        if self.status == "disappearing":
            if self.reverse:
                self.rect.x -= self.speed.x
                self.rect.y -= self.speed.y
                if self.rect.x <= self.originposvec.x - self.distance.x:
                    self.rect.x = self.originposvec.x - self.distance.x
                if self.rect.y <= self.originposvec.y - self.distance.y:
                    self.rect.y = self.originposvec.y - self.distance.y
                if (self.rect.x , self.rect.y) == self.originposvec - self.distance:
                    self.status = "done"
            else:
                self.rect.x += self.speed.x
                self.rect.y += self.speed.y
                if self.rect.x >= self.originposvec.x + self.distance.x:
                    self.rect.x = self.originposvec.x + self.distance.x
                if self.rect.y >= self.originposvec.y + self.distance.y:
                    self.rect.y = self.originposvec.y + self.distance.y
                if (self.rect.x , self.rect.y) == self.originposvec + self.distance:
                    self.status = "done"
        self.image.set_alpha(255-((self.rect.x , self.rect.y)-self.originposvec).length()/self.distance.length()*255)

class CharacterDrawSprite(LimitTimePic):  # 为什么sprite还有立绘的意思。。。
    def __init__(self, image, posvec):
        self.image = image
        super().__init__(self.image, posvec, 120)

    def update(self):
        self.rect.centery -= (abs(self.lastlifetime - 60)/10)**2
        super().update()


class SpellNameSprite(LimitTimePic):  # 符卡名称显示类 同下
    def __init__(self, image, posvec, lifetime, enemy, spellid):
        super().__init__(image, posvec, lifetime)
        self.enemy = enemy
        self.spellid = spellid
        self.originimage = self.image.copy()
        self.acc = -0.1
        self.speed = 2
        self.is_created_scoretext = False

    def update(self):
        if self.rect.y > 70:
            self.rect.y -= max(5, 10 + self.speed)
            self.image = self.originimage.copy()
            pygame.transform.scale(self.image, (self.image.get_width(
            )*(1+self.speed*1), self.image.get_height()*(1+self.speed*1)))  # 由大变小 高度耦合
            self.rect.x = self.posvec[0] - self.image.get_width()
            self.image.set_alpha(255 - self.speed*20)  # 由虚变实 高度耦合
            return
        if not self.is_created_scoretext:  # 在下方显示分数
            self.image.set_alpha(255)
            text = gameui.font_12.render(
                "SCORE:"+str((self.enemy.spelldata[self.enemy.spell].time - self.enemy.spelltick) * 1000), True, "BLACK")
            self.scoretext = LimitTimePic(text, (self.rect.x + text.get_width(
            )/2, self.rect.y + self.image.get_height() + text.get_height()), -1)  # 传入的应是分数文字所在的中心坐标
            effectgroup.add(self.scoretext)
            self.is_created_scoretext = True
        if not player_Character.missinthisspell:
            self.scoretext.image = gameui.font_12.render(
                "SCORE:"+str((self.enemy.spelldata[self.enemy.spell].time - self.enemy.spelltick) * 1000), True, "BLACK")
        else:
            self.scoretext.image = gameui.font_12.render(
                "FAILED...", True, "BLACK")
        if self.enemy.spell > self.spellid:
            self.scoretext.kill()
            self.kill()


class Tempbar(LimitTimePic):  # 温度槽类 应该放在ui类里的 但是就这样吧
    def __init__(self, image, posvec, lifetime, character):
        super().__init__(image, posvec, lifetime)
        self.character = character
        self.originimage = self.image
        self.alpha = 255

    def update(self):
        self.image = self.originimage.copy()
        self.image.blit(self.originimage, (0, 0))
        pygame.draw.rect(self.image, "BLUE", [int(
            self.character.temperature / 1000) + 1, 1, 80-int(self.character.temperature / 1000), 9])
        if pygame.sprite.collide_circle(player_CharacterImage, self):
            self.alpha = max(self.alpha-10, 100)  # 渐变效果
            self.image.set_alpha(self.alpha)
        else:
            self.alpha = min(self.alpha+10, 255)
            self.image.set_alpha(self.alpha)


class Spellcard:  # 符卡结构体
    def __init__(self, name: str, hp: int, isspell: bool, time: int, shootcooldown):
        self.name = name
        self.hp = hp
        self.isspell = isspell
        self.time = time
        self.shootcooldown = shootcooldown


class Enemy(pygame.sprite.Sprite):  # 敌人类
    def __init__(self, maxHP, posvec):
        super().__init__()
        self.enter_spell8 = False
        self.ice_cone_image = picloader.load("Picture/ice_cone.bmp")
        self.spelldata = [
            Spellcard("缺省", 4000, False, 2400, 1),  # 符卡从第一张开始算 所以从[1]开始访问
            Spellcard("缺省", 400, False, 2400, 1),
            Spellcard("冷符「冷冻锁链」", 4000, True, 2400, 10),
            Spellcard("符卡1", 4000, False, 2400, 4),
            Spellcard("冻符「超完美冻结」", 4000, True, 2400, 1),
            Spellcard("符卡1", 4000, False, 2400, 1),
            Spellcard("寒符「幻想乡的寒极」", 4000, True, 2400, 1),
            Spellcard("符卡1", 4000, False, 2400, 1),
            Spellcard("草&雪符「忍冬草」", 4000, True, 2400, 1),
            Spellcard("冰符「Grand Ice Ball」", 4000, True, 2400, 1)
        ]
        self.spell = 1
        self.HP = self.spelldata[self.spell].hp
        self.image = picloader.load("Picture/cirno.bmp")
        self.rect = self.image.get_rect()
        self.maxHP = maxHP
        self.posvec = posvec
        self.rect.centerx, self.rect.centery = self.posvec
        self.speedvec = V2(0, 0)
        self.width = 59
        self.height = 74
        self.shootCoolDownCount = 0
        self.spellcount = 10
        self.spelltick = 0
        self.enter_spell6 = False  # 屎
        self.recovering = False
        self.mover = SpriteMover(self)
        self.recovermover = SpriteMover(self)
        self.mover.reload([
            MoveData.Sleep(60)
        ])
        self.recovermover.reload([
            MoveData.Sleep(60)
        ])

    def update(self):
        if self.recovering:
            self.recover()
            self.recovermover.update()
            return
        self.mover.update()  # 处理移动
        global score
        self.shootCoolDownCount += 1
        self.spelltick += 1
        if self.spelldata[self.spell].shootcooldown == self.shootCoolDownCount:  # 控制shoot函数执行间隔
            self.shoot()
            self.shootCoolDownCount = 0
        list = pygame.sprite.spritecollide(
            self, selfBulletGroup, False)  # 伤害判定
        for item in list:
            if self.HP/self.spelldata[self.spell].hp < 0.1:
                if not item.free:
                    se.play("damageloud")
            else:
                if not item.free:
                    se.play("damage")
            self.HP -= item.damage
            player_Character.temperature += item.damage  # 子弹打出伤害加温度
            if not item.free:
                item.kill()
        # 本张符卡/非符结束判定
        if self.HP < 0 or self.spelltick >= self.spelldata[self.spell].time:
            se.play("destory", se.ENEMY_DESTORY_CHANNEL)
            if self.spelldata[self.spell].isspell == True:  # 不是非符才能收
                if not player_Character.missinthisspell:  # 符卡收取判定
                    spellscore = (
                        self.spelldata[self.spell].time - self.spelltick) * 1000
                    score += spellscore
                    player_Character.temperature += 3000 + spellscore / 100  # 收卡加温度
                    effectgroup.add(LimitTimePic(
                        gameui.bonustext, (gameZoneRight-(gameZoneRight-gameZoneLeft)/2, 270), 120))
                    scoretext = gameui.font_24.render(
                        str(spellscore), True, (0, 128, 240))
                    effectgroup.add(LimitTimePic(
                        scoretext, (gameZoneRight-(gameZoneRight-gameZoneLeft)/2, 300), 120))
                else:
                    effectgroup.add(LimitTimePic(
                        gameui.bonusfailedtext, (gameZoneRight-(gameZoneRight-gameZoneLeft)/2, 300), 120))
            if self.spell > self.spellcount:
                self.kill()
                return
            self.recovering = True
            self.spellinit()  # 此时已经进入下张符卡
            return

    def spellinit(self):  # 高耦合屎山
        self.spelltick = 0
        self.spell += 1
        player_Character.missinthisspell = False
        if self.spell == 2:
            self.mover.reload([
                MoveData.MoveBetween(
                    1, [(gameZoneLeft+100, 100), (gameZoneRight-100, 100)])
            ])
        if self.spell == 4:
            self.isfreeze = False
            self.recovermover.reload([
                MoveData.MoveInTime(60, (gameZoneLeft + 100, 100))
            ])
            self.mover.reload([
                MoveData.MoveInTime(400, (gameZoneRight - 100, 100)),
                MoveData.MoveInTime(100, (gameZoneLeft + 100, 100)),
                MoveData.Sleep(100)
            ])
        if self.spell == 5:
            self.recovermover.reload([
                MoveData.MoveInTime(60, (gameZoneLeft + 100, gameZoneUp - 100))
            ])
            self.mover.reload([
                MoveData.MoveInTime(
                    300, (gameZoneRight - 100, gameZoneUp - 100)),
                MoveData.MoveInTime(
                    300, (gameZoneRight - 100, gameZoneDown + 100)),
                MoveData.MoveInTime(
                    300, (gameZoneLeft + 100, gameZoneDown + 100)),
                MoveData.MoveInTime(
                    300, (gameZoneLeft + 100, gameZoneUp - 100))
            ])
        if self.spell == 6:
            self.recovermover.reload([
                MoveData.MoveInTime(60, (gameZoneCenterX, gameZoneCenterY))
            ])
            self.mover.reload([
                MoveData.Sleep(60)
            ])
        if self.spell == 8:
            self.spell8_bulletrotate = 3

    def recover(self):
        pygame.sprite.spritecollide(self, selfBulletGroup, False)  # 无敌
        self.HP += self.spelldata[self.spell].hp / 60  # 恢复完成则继续正常行动
        for item in enemyBulletGroup:
            if (item.rect.center[0]-self.rect.center[0])**2 + (item.rect.center[1]-self.rect.center[1])**2 < ((self.HP / self.spelldata[self.spell].hp) * 4 * 900)**2:
                # 在30帧内以笨蛋为圆心创建一个半径为3600的把弹幕转换为道具的圆的狗屎实现
                item.tobulletitem()
        if self.HP >= self.spelldata[self.spell].hp:
            self.recovering = False
            self.HP = self.spelldata[self.spell].hp
            self.shootCoolDownCount = 0
            se.play("bomb", se.ENEMY_SPELL_CHANNEL)
            if self.spelldata[self.spell].isspell == True:
                text = gameui.font_24.render(
                    self.spelldata[self.spell].name, True, "BLACK")
                effectgroup.add(CharacterDrawSprite(
                    gameui.cirno, (650 - gameui.cirno.get_width()/2, 900 + gameui.cirno.get_height()/2)))
                effectgroup.add(SpellNameSprite(
                    text, (500+text.get_width()/2, 800), -1, self, self.spell))  # 符卡宣告动画

    def shoot(self):
        if self.spell == 1:
            tmp_vec1 = V2(
                random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * 3
            enemyBulletGroup.add(
                Bullet(1, ((random.randint(0, 240)), (random.randint(0, 240)), (random.randint(
                    0, 240))), 20, 20, V2(self.posvec.x, self.posvec.y), tmp_vec1, 1, 0, 0, V2(0, 0)),
                Bullet(1, ((random.randint(0, 240)), (random.randint(0, 240)), (random.randint(
                    0, 240))), 20, 20, V2(self.posvec.x, self.posvec.y), tmp_vec1, 1, 0, 0, V2(0, 0))
            )

        if self.spell == 2:
            if not self.spelltick % 300 < 20:
                for i in range(-4, 5, 1):  # 上下2*9=18条封位弹
                    enemyBulletGroup.add(
                        Bullet(1, (100, 128, 240), 20, 20, V2(
                            self.posvec.x, self.posvec.y), V2(i, 2), 1, 0, 0, V2(0, 0)),
                        Bullet(1, (100, 128, 240), 20, 20, V2(
                            self.posvec.x, self.posvec.y), V2(i, -2), 1, 0, 0, V2(0, 0))
                    )
            if self.spelltick / 10 % 3:  # 8颗朝下的随机弹
                for i in range(8):
                    enemyBulletGroup.add(
                        Bullet(1, ((random.randint(0, 240)), (random.randint(0, 240)), (random.randint(0, 240))), 20, 20, V2(
                            self.posvec.x, self.posvec.y), V2(random.uniform(3, -3), 3), 1, 0, 0, V2(0, 0))
                    )
            if self.spelltick % 120 == 0:  # 1颗自机狙
                enemyBulletGroup.add(
                    Bullet(1, (240, 240, 240), 60, 60, V2(
                        self.posvec.x, self.posvec.y), relative_direction(self, player_Character)*5, 1, 0, 0, V2(0, 0))
                )

        if self.spell == 3:  # 大冰棱子
            enemyBulletGroup.add(
                Bullet(self.ice_cone_image.copy(), ((random.randint(0, 240)), (random.randint(0, 240)), (random.randint(0, 240))), 40, 40, V2(
                    random.uniform(10, 600), self.rect.centery - 50), V2(0, 1.5), 1, 0, 0, V2(0, 0.01))
            )
            if self.spelltick % 90 == 0:  # 屎山偶数弹
                enemyBulletGroup.add(
                    Bullet(1, (240, 240, 240), 60, 60, V2(self.posvec.x, self.posvec.y), relative_direction(
                        self, player_Character).rotate(10)*8, 1, 0, 0, V2(0, 0)),
                    Bullet(1, (240, 240, 240), 60, 60, V2(self.posvec.x, self.posvec.y), relative_direction(
                        self, player_Character).rotate(-10)*8, 1, 0, 0, V2(0, 0))
                )

        if self.spell == 4:
            if self.spelltick % 600 < 400:
                if self.isfreeze:
                    self.isfreeze = False
                    for item in enemyBulletGroup:
                        item.accvec = V2(
                            random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * 0.02
                        sprite_disappear(item, 120)
                # 全向随机弹
                tmp_vec1 = V2(
                    random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                bullet = Bullet(1, ((random.randint(0, 240)), (random.randint(0, 240)), (random.randint(0, 240))), 20, 20, V2(
                    self.posvec.x, self.posvec.y), tmp_vec1 * random.uniform(1.5, 2.5), 1, 0, 0, V2(0, 0))
                enemyBulletGroup.add(bullet)
            else:
                if self.spelltick % 10 == 0 and 410 < self.spelltick % 600 < 500:  # 2*⑨ = 18颗偶数弹
                    enemyBulletGroup.add(
                        Bullet(1, (20, 100, 240), 40, 40, V2(self.posvec.x, self.posvec.y), relative_direction(
                            self, player_Character).rotate(random.uniform(5, 15))*8, 1, 0, 0, V2(0, 0)),
                        Bullet(1, (20, 100, 240), 40, 40, V2(self.posvec.x, self.posvec.y), relative_direction(
                            self, player_Character).rotate(random.uniform(-5, -15))*8, 1, 0, 0, V2(0, 0))
                    )
                if not self.isfreeze:  # Perfect Freeze!
                    self.isfreeze = True
                    for item in enemyBulletGroup:
                        item.isfreezebullet = True
                        pygame.draw.circle(
                            item.image, (240, 240, 240), (item.width/2, item.height/2), item.width/2)
                        pygame.draw.circle(
                            item.image, "WHITE", (item.width/2, item.height/2), item.width/3)
                        pygame.draw.circle(
                            item.image, 'WHITE', (item.width/2, item.height/2), item.width/2-2, 1)
                        item.speedvec = V2(0, 0)

        if self.spell == 5:
            if self.spelltick % 30 == 0:
                for i in range(60):
                    bullet = Bullet(1, (0, 100, 240), 20, 20, V2(
                        i * 60, 0), V2(0, 2), 1, 0, 0, V2(0, 0))
                    bullet.tracktime = 181
                    enemyBulletGroup.add(bullet)
            if self.spelltick % 30 == 0:  # 一定时间内的诱导弹
                se.play("enemyst02")
                bullet = Bullet(1, (240, 240, 240), 40, 40, V2(self.posvec.x, self.posvec.y), relative_direction(
                    self, player_Character) * 2, 1, 0, 0, V2(0, 0))
                bullet.tracktime = 0
                enemyBulletGroup.add(bullet)
            for item in enemyBulletGroup:
                if hasattr(item, "tracktime"):
                    if item.tracktime > 150:  # 超过时间就停止追踪
                        continue
                    item.tracktime += 1
                    directvec = relative_direction(item, player_Character)
                    if 0 < item.speedvec.angle_to(directvec) < 180:
                        item.speedvec.rotate_ip(2)
                    else:
                        item.speedvec.rotate_ip(-2)

        if self.spell == 6:  # 转圈弹
            enemyBulletGroup.add(
                Bullet(1, (0, 100, 240), 15, 15, V2(self.posvec.x, self.posvec.y), V2(
                    0, 2).rotate(self.spelltick * 18), 1, 0, 0, V2(0, 0)),
                Bullet(1, (0, 100, 240), 15, 15, V2(self.posvec.x, self.posvec.y), V2(
                    0, 2).rotate(self.spelltick * 9), 1, 0, 0, V2(0, 0))
            )
            if self.spelltick % 90 == 0:  # 1颗自机狙
                bullet = Bullet(1, (240, 240, 240), 40, 40, V2(
                    self.posvec.x, self.posvec.y), relative_direction(self, player_Character)*4, 1, 0, 0, V2(0, 0))
                enemyBulletGroup.add(bullet)

        if self.spell == 7:
            for i in range(60):
                if self.spelltick % 15 == i:  # 开花旋转加速弹（?
                    tmp_speedvec = V2(
                        0, -1).rotate(i * 24 + (self.spelltick / 5) % 360)
                    bullet = Bullet(1, (0, min(240 - self.spelltick % 240, self.spelltick % 240) * 2, 240),
                                    20, 20, self.posvec + tmp_speedvec, tmp_speedvec, 1, 0, 0, tmp_speedvec * 0.02)
                    enemyBulletGroup.add(bullet)
                if (self.spelltick + 5) % 15 == i:
                    tmp_speedvec = V2(
                        0, -1).rotate(i * 24 + (self.spelltick / 5) % 360)
                    bullet = Bullet(1, (0, min(240 - self.spelltick % 240, self.spelltick % 240) * 2, 240),
                                    20, 20, self.posvec + tmp_speedvec, tmp_speedvec, 1, 0, 0, tmp_speedvec * 0.04)
                    enemyBulletGroup.add(bullet)
                if (self.spelltick + 10) % 15 == i:
                    tmp_speedvec = V2(
                        0, -1).rotate(i * 24 + (self.spelltick / 5) % 360)
                    bullet = Bullet(1, (0, min(240 - self.spelltick % 240, self.spelltick % 240) * 2, 240),
                                    20, 20, self.posvec + tmp_speedvec, tmp_speedvec, 1, 0, 0, tmp_speedvec * 0.06)
                    enemyBulletGroup.add(bullet)

        if self.spell == 8:
            if self.spelltick % 2 == 0:
                self.posvec = V2(
                    self.rect.centerx, self.rect.centery)
                self.speedvec = V2(
                    0, 0)  # 防止弹幕修改笨蛋位置只能每帧锁定速度了
                bullet = Bullet(1, (0, 100, 240), 20, 20, self.posvec, V2(
                    random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * random.uniform(4, 5), 1, 0, 0, V2(0, 0))
                bullet.tracktime = 0
                enemyBulletGroup.add(bullet)
            if self.spelltick % 2 == 1:
                self.posvec = V2(
                    self.rect.centerx, self.rect.centery)
                bullet = Bullet(1, (0, 240, 100), 20, 20, self.posvec, V2(
                    random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * random.uniform(3, 4), 1, 0, 0, V2(0, 0))
                bullet.tracktime = 0
                enemyBulletGroup.add(bullet)
                self.posvec = V2(
                    self.rect.centerx, self.rect.centery)
                bullet = Bullet(1, (240, 240, 240), 20, 20, self.posvec, V2(
                    random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * random.uniform(2, 3), 1, 0, 0, V2(0, 0))
                bullet.tracktime = 0
                enemyBulletGroup.add(bullet)
            for item in enemyBulletGroup:
                if item.tracktime > 180:  # 超过时间就停止旋转
                    continue
                item.tracktime += 1
                item.speedvec.rotate_ip(self.spell8_bulletrotate)
            if self.spelltick % 480 == 0:
                self.spell8_bulletrotate = -self.spell8_bulletrotate
                se.play("enemyst01")
                for item in enemyBulletGroup:
                    item.tracktime = 999
            self.posvec = V2(
                self.rect.centerx, self.rect.centery)

        if self.spell == 9:
            if self.spelltick % 30 == 0:
                for i in range(30):  # 白色奇数弹
                    tmpspeed_vec = (relative_direction(
                        self, player_Character)*4).rotate(i * 12)
                    bullet = Bullet(1, (240, 240, 240), 20, 20, V2(
                        self.posvec.x, self.posvec.y) + tmpspeed_vec, tmpspeed_vec, 1, 0, 0, V2(0, 0))
                    enemyBulletGroup.add(bullet)
            if self.spelltick % 30 == 15:
                for i in range(30):  # 蓝色偶数弹
                    tmpspeed_vec = (relative_direction(
                        self, player_Character)*4).rotate(i * 12 + 96)
                    bullet = Bullet(1, (0, 120, 240), 20, 20, V2(
                        self.posvec.x, self.posvec.y) + tmpspeed_vec, tmpspeed_vec, 1, 0, 0, V2(0, 0))
                    enemyBulletGroup.add(bullet)
            if not self.spelltick % 180:  # 创建变大弹幕
                self.color_list = [
                    min(80 - 2*i, 2*i) * 6 for i in range(40)] + [0 for i in range(20)]  # 懒 直接生成局部变量
                self.stand = True
                bullet = Bullet(1, (0, 0, 0), 10, 10, V2(
                    self.posvec.x, self.posvec.y) + V2(0, 10), (0, 0), 1, 0, 0, V2(0, 0))
                bullet.specialtag_1 = True
                enemyBulletGroup.add(bullet)
            if 0 < self.spelltick % 180 < 60:  # 不断变大变炫彩
                tmp_tick = self.spelltick % 60
                for item in enemyBulletGroup:
                    if hasattr(item, "specialtag_1") and item.specialtag_1 == True:
                        enemyBulletGroup.remove(item)
                        bullet = Bullet(1, (self.color_list[tmp_tick], self.color_list[tmp_tick - 20], self.color_list[tmp_tick - 40]), 10 + tmp_tick * 3, 10 + tmp_tick * 3, V2(
                            self.posvec.x, self.posvec.y) + V2(0, 10 - tmp_tick), V2(0, 0), 1, 0, 0, V2(0, 0))
                        bullet.specialtag_1 = True
                        enemyBulletGroup.add(bullet)
            if self.spelltick % 180 == 60:  # 丢出去
                se.play("enemyst01")
                self.stand = False
                for item in enemyBulletGroup:
                    if hasattr(item, "specialtag_1") and item.specialtag_1 == True:
                        item.specialtag_1 = False
                        item.speedvec = relative_direction(
                            self, player_Character)*4
                        item.accvec = relative_direction(
                            self, player_Character)*0.1


class TimeRecorder:  # 基于pygame计时器的性能监测类
    _starttick = 0

    def start(self):
        self._starttick = pygame.time.get_ticks()

    def stop(self, name: str, start: bool):
        print("{0}:{1}ms".format(name, pygame.time.get_ticks()-self._starttick))
        if start:
            self.start()


class Characterctl():
    def __init__(self, character, characterOptionLeft, characterOptionRight, characterImage):
        self.character = character
        self.characterOptionLeft = characterOptionLeft
        self.characterOptionRight = characterOptionRight
        self.characterImage = characterImage

    def keydown(self, key):
        if key == pygame.K_UP:
            self.character.upspeed = 1
        if key == pygame.K_DOWN:
            self.character.downspeed = 1
        if key == pygame.K_LEFT:
            self.character.leftspeed = 1
            self.characterImage.leftspeed = 1
        if key == pygame.K_RIGHT:
            self.character.rightspeed = 1
            self.characterImage.rightspeed = 1
        if key == pygame.K_z:
            self.character.shoot = True
            self.characterOptionLeft.shoot = True
            self.characterOptionRight.shoot = True
        if key == pygame.K_x:
            if not self.character.status == "bombing" and self.character.Bomb > 0 and self.character.temperature > 0:  # 温度为0不能放b
                self.character.status = "usebomb"
        if key == pygame.K_LSHIFT:
            self.character.setmode(mode=1)
            self.characterOptionLeft.slow = True
            self.characterOptionRight.slow = True
        if key == pygame.K_ESCAPE:
            global done
            done = True
        if key == pygame.K_c:
            if self.character.temperature < 50000 and self.character.Bomb > 0:
                self.character.Bomb -= 1
                se.play("spellextend", se.SPELL_EXTEND_CHANNEL)
                self.character.temperature += 30000

    def keyup(self, key):
        if key == pygame.K_UP:
            self.character.upspeed = 0
        if key == pygame.K_DOWN:
            self.character.downspeed = 0
        if key == pygame.K_LEFT:
            self.character.leftspeed = 0
            self.characterImage.leftspeed = 0
        if key == pygame.K_RIGHT:
            self.character.rightspeed = 0
            self.characterImage.rightspeed = 0
        if key == pygame.K_z:
            self.character.shoot = False
            self.characterOptionLeft.shoot = False
            self.characterOptionRight.shoot = False
        if key == pygame.K_LSHIFT:
            self.character.setmode(mode=0)
            self.characterOptionLeft.slow = False
            self.characterOptionRight.slow = False

# 返回从Sprite1指向Sprite2的单位向量 若为0向量则返回随机微小向量
def relative_direction(sprite1: pygame.sprite.Sprite, sprite2: pygame.sprite.Sprite):
    if (sprite2.rect.centerx - sprite1.rect.centerx) == 0 and (sprite2.rect.centery - sprite1.rect.centery) == 0:
        return V2(random.uniform(-0.001, 0.001), random.uniform(0.001, -0.001))
    return V2(sprite2.rect.centerx - sprite1.rect.centerx, sprite2.rect.centery - sprite1.rect.centery).normalize()

# 令sprite在disappeartime里逐渐消失
def sprite_disappear(sprite: pygame.sprite.Sprite, disappeartime: int):
    if not sprite in disappear_group:
        sprite.disappeartime = sprite.nowdisappeartime = disappeartime
        disappear_group.add(sprite)

def create_setting():  # 生成配置文件
    settings = {"powersave": False, "sevol": 0.2, "bgmvol": 0.2}
    with open("settings.json", "w") as file:
        file.write(json.dumps(settings))
    return settings

def create_playerdata():  # 生成玩家数据
    playerdata = {"reimu":[], "marisa":[]}
    playerdata_gzip = gzip.compress(json.dumps(playerdata).encode())
    with gzip.open('./player.dat', 'wb') as file:
        file.write(playerdata_gzip)
    return playerdata

def mainbgdraw():
    global mainbgposy
    screen.blit(gameui.mainbackground, (0, mainbgposy))
    mainbgposy += mainbgspeedy
    mainbgposy = min(0,mainbgposy)
    mainbgposy = max(-720,mainbgposy)

def reset(playreplay = False):  
    global choosecharacter, picloader, seed, input_event_list, jsondict,score,replayeventcount
    global disappear_group, self_group, enemyGroup, selfBulletGroup, enemyBulletGroup, bombgroup, effectgroup, itemGroup
    global player_Character, player_CharacterImage, player_CharacterOptionLeft, player_CharacterOptionRight, baka,characterctl,tempbar,player_bomb_pictures
    picloader = asset.PicLoader()
    score = 0
    if playreplay:
        seed = jsondict["metadata"]["seed"]
        choosecharacter = jsondict["metadata"]["character"]
    else:
        seed = random.randint(1000000000, 9999999999)  # 下面在为replay做准备
        input_event_list = []
        jsondict = {  # 初始化录像数据结构
            "metadata":
            {
                "seed": seed,
                "character": choosecharacter,
                "time": int(time.time()),
                "avgfps": 57,
                "score": 0,
                "playername":"TJUGERKFER"
            },
            "replaybody": {
                "tick": [],
                "type": [],
                "key": []
            }
        }
    random.seed(seed)
    disappear_group = pygame.sprite.Group()
    self_group = pygame.sprite.Group()
    enemyGroup = pygame.sprite.Group()
    selfBulletGroup = pygame.sprite.Group()
    enemyBulletGroup = pygame.sprite.Group()
    bombgroup = pygame.sprite.Group()
    effectgroup = pygame.sprite.Group()
    itemGroup = pygame.sprite.Group()

    if choosecharacter == "Reimu":
        player_Character = playerCharacter(
            5, 8, 0.4, 10, 3, 30000, 27, "梦符「梦想封印·彩」", gameui.reimu)
        player_CharacterImage = playerCharacterImage(
            picloader.load("Picture/reimu_new.bmp", 35, 50), picloader.load("Picture/reimu_newl.bmp", 35, 50), picloader.load("Picture/reimu_newr.bmp", 35, 50))
        player_CharacterOptionRight = playerOption(
            picloader.load("Picture/reimu_option.bmp"), 27, 28, 9, 6)
        player_CharacterOptionLeft = playerOption(
            picloader.load("Picture/reimu_option.bmp"), -27, 28, 9, 6)
        player_Character.spell_image = picloader.load(
            "Picture/reimu_spell.bmp")
        player_Character.spell_purple_image = picloader.load(
            "Picture/reimu_spell_purple.bmp")
        player_Character.spell_blue_image = picloader.load(
            "Picture/reimu_spell_blue.bmp")

        # 这段是Bing AI优化的
        colors = ["red", "orange", "yellow", "green", "blue", "purple"]
        player_bomb_pictures = {}
        for color in colors:
            filename = "Picture/bigjade_" + color + ".bmp"
            picture = picloader.load(filename)
            player_bomb_pictures[color] = picture

    if choosecharacter == "Marisa":
        player_Character = playerCharacter(
            6, 9, 0.3, 9, 6, 30000, 30, "魔符「Blasting Star」", gameui.marisa)
        player_Character.bulletimage = picloader.load(
            "Picture/marisa_fire.bmp", 20, 36)
        player_CharacterImage = playerCharacterImage(
            picloader.load("Picture/marisa_new.bmp", 35, 50), picloader.load("Picture/marisa_newl.bmp", 35, 50), picloader.load("Picture/marisa_newr.bmp", 35, 50))
        player_CharacterOptionRight = playerOption(
            picloader.load("Picture/marisa_option.bmp", hasalpha=True), 27, 28, 0, 8)
        player_CharacterOptionLeft = playerOption(picloader.load(
            "Picture/marisa_option.bmp", hasalpha=True), -27, 28, 0, 8)
        player_Character.missile_image = picloader.load(
            "Picture/marisa_missile.bmp")
        colors = ["red", "green", "yellow"]
        player_bomb_pictures = {"red": [], "yellow": [], "green": []}
        for color in colors: 
            filename = "Picture/bigstar_" + color + ".bmp"
            picture = picloader.load(filename)
            for i in range(121):
                player_bomb_pictures[color].append(
                    pygame.transform.rotate(picture, i*3))

    self_group.add(player_CharacterImage)
    self_group.add(player_CharacterOptionRight)
    self_group.add(player_CharacterOptionLeft)
    self_group.add(player_Character)
    characterctl = Characterctl(player_Character, player_CharacterOptionLeft,
                                player_CharacterOptionRight, player_CharacterImage)
    tempbar = Tempbar(gameui.tempbar, (550, 670), -1, player_Character)
    effectgroup.add(tempbar)
    baka = Enemy(5000, V2(gameZoneCenterX, 100))
    enemyGroup.add(baka)

def charactermenu():
    global choosecharacter,jsondict
    choosecharacter = "Reimu"
    appeareffectgroup = pygame.sprite.Group()
    titleENG = LimitTimePic(gameui.font_36.render("Player Select",True,"WHITE"),(130,50)) # 还能有比以下若干行代码更屎山的玩意吗。。。
    titleENGS = LimitTimePic(gameui.font_36.render("Player Select",True,"BLACK"),(128,48))
    titleZHS = LimitTimePic(gameui.font_24.render("选择人类",True,"GREY"),(130,80))
    titleZHSS = LimitTimePic(gameui.font_24.render("选择人类",True,"BLACK"),(128,78))
    reimupic = PictureAppearEffect(gameui.mainmenureimu,V2(10,0),V2(500,120),False,V2(200,0),"appearing") 
    marisapic = PictureAppearEffect(gameui.mainmenumarisa,V2(10,0),V2(500,120),False,V2(200,0),"disappeared")
    reimuname = PictureAppearEffect(gameui.font_28.render("博丽灵梦",True,"RED"),V2(13,0),V2(600,100),False,V2(250,0),"appearing")
    marisaname = PictureAppearEffect(gameui.font_28.render("雾雨魔理沙",True,"YELLOW"),V2(13,0),V2(550,100),False,V2(250,0),"disappeared")
    reimutitle = PictureAppearEffect(gameui.font_20.render("乐园的可爱巫女",True,"WHITE"),V2(15,0),V2(550,80),False,V2(300,0),"appearing")
    marisatitle = PictureAppearEffect(gameui.font_20.render("东洋的西洋魔法使",True,"WHITE"),V2(15,0),V2(500,80),False,V2(300,0),"disappeared")
    reimudesc = PictureAppearEffect(gameui.reimudesc,V2(15,0),V2(120,200),True,V2(300,0),"appearing")
    marisadesc = PictureAppearEffect(gameui.marisadesc,V2(15,0),V2(120,200),False,V2(300,0),"disappeared")
    belongtomarisa = [marisadesc,marisapic,marisaname,marisatitle]
    belongtoreimu = [reimudesc,reimupic,reimuname,reimutitle]
    appeareffectgroup.add(reimupic,marisapic,reimuname,marisaname,reimutitle,marisatitle,reimudesc,marisadesc,titleENGS,titleENG,titleZHSS,titleZHS)
    waittick = 0
    def changetomarisa(reverse):
        global choosecharacter
        choosecharacter = "Marisa"
        marisadesc.reverse = not reverse
        marisadesc.appear()
        for item in belongtomarisa[1:]:
            item.reverse = reverse
            item.appear()
        reimudesc.reverse = not reverse
        reimudesc.disappear()
        for item in belongtoreimu[1:]:
            item.reverse = reverse
            item.disappear()

    def changetoreimu(reverse):
        global choosecharacter
        choosecharacter = "Reimu"
        reimudesc.reverse = not reverse
        reimudesc.appear()
        for item in belongtoreimu[1:]:
            item.reverse = reverse
            item.appear()
        marisadesc.reverse = not reverse
        marisadesc.disappear()
        for item in belongtomarisa[1:]:
            item.reverse = reverse
            item.disappear()

    while True:
        mainbgdraw()
        clock.tick(60)
        waittick += 1
        if waittick < 36: # 等待画面完全落下
            pygame.display.flip()
            continue
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    se.play("select")
                    if choosecharacter == "Reimu":
                        changetomarisa(True)
                    else:
                        changetoreimu(True)
                if event.key == pygame.K_RIGHT:
                    se.play("select")
                    if choosecharacter == "Reimu":
                        changetomarisa(False)
                    else:
                        changetoreimu(False)
                if event.key == pygame.K_z:
                    jsondict = False
                    reset()
                    gameloop()
                    return
                if event.key == pygame.K_x or event.key == pygame.K_ESCAPE:
                    return
        appeareffectgroup.update()
        appeareffectgroup.draw(screen)
        pygame.display.flip()

def loadreplaydata():
    jsondictlist = [False for i in range(25)]
    for i in range(24):
        if not os.path.exists("./replay/thxxx_"+str(i+1).zfill(2)+".rpy") :
            continue
        with gzip.open("./replay/thxxx_"+str(i+1).zfill(2)+".rpy", 'rb') as f:
            jsondictlist[i]=json.loads(gzip.decompress(
                f.read()).decode(), strict=False)
    return jsondictlist

def savereplay(screenshot,endmask):
    global jsondict
    def reload():
        jsondictlist = loadreplaydata()
        menustructlist = [asset.MenuStruct("NO." + str(i).zfill(2),True) for i in range(26)] # 菜单第一项存放表头
        menustructlist[0] = asset.MenuStruct("NO.XX" + "   " + "  TIME   " + "  "+ "PLAYERNAME"  + " CHARACTER  " + "PLR ",True)
        for i,e in enumerate(jsondictlist):
            if not jsondictlist[i]: # 第一项用来放表头了
                menustructlist[i+1] = asset.MenuStruct("NO." + str(i+1).zfill(2) + "   " + "--/--/--" + "   "+ "----------" + "   " + "------" + "   " + "---%")
                continue
            menustructlist[i+1] = asset.MenuStruct("NO." + str(i+1).zfill(2) + "   " + time.strftime("%y/%m/%d", time.localtime(e["metadata"]["time"])) + "   "+ e["metadata"]["playername"].ljust(10) + "   " + e["metadata"]["character"].ljust(6) + "   "  + "{0:.1f}%".format((1 - min(1,e["metadata"]["avgfps"]/60))*100))
            if i==25:break
        mymenu = asset.Menu(gameui.font_mono_20,menustructlist,"WHITE", "YELLOW","GREY",(50, 100),linesep=-5,defaultchoice=1)
        titleENG = LimitTimePic(gameui.font_24.render("Slot Select",True,"WHITE"),(130,50)) # repetition good
        titleENGS = LimitTimePic(gameui.font_24.render("Slot Select",True,"BLACK"),(128,48))
        titleZHS = LimitTimePic(gameui.font_24.render("选择一个槽位",True,"GREY"),(130,85))
        titleZHSS = LimitTimePic(gameui.font_24.render("选择一份槽位",True,"BLACK"),(128,83))
        mymenu.optiongroup.add(titleENGS,titleENG,titleZHSS,titleZHS)
        return mymenu
    mymenu = reload()
    while True:
        save = False
        screen.blit(screenshot,(0,0))
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    se.play("select")
                    mymenu.up()
                if event.key == pygame.K_DOWN:
                    se.play("select")
                    mymenu.down()
                if event.key == pygame.K_z: 
                    se.play("select")
                    slot = mymenu.choose()
                    done = False
                    tmpplayername = ""

                    while not done: # 开始噩梦嵌套 全屎山最屎代码
                        mymenu.getelementbyid(slot).settext("NO." + str(slot).zfill(2) + "   " + time.strftime("%y/%m/%d", time.localtime(jsondict["metadata"]["time"])) + "   "+ tmpplayername.ljust(10,"_") + "   " + jsondict["metadata"]["character"].ljust(6) + "   "  + "{0:.1f}%".format((1 - min(1,jsondict["metadata"]["avgfps"]/60))*100))
                        screen.blit(screenshot,(0,0))
                        clock.tick(60)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                exit()
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_RETURN:
                                    se.play("extend")
                                    jsondict["metadata"]["playername"] = tmpplayername # 跳出循环并保存玩家机签
                                    done = True
                                    save = True
                                elif event.key == pygame.K_BACKSPACE:
                                    se.play("select")
                                    if len(tmpplayername) == 0:continue # 长度为0就不删
                                    tmpplayername = tmpplayername[:-1]
                                elif event.key == pygame.K_ESCAPE: # 跳出循环并重置录像菜单
                                    se.play("cancel")
                                    mymenu = reload()
                                    done = True
                                else:
                                    se.play("select")
                                    tmpplayername += event.unicode
                                    if len(tmpplayername) > 10:
                                        tmpplayername = tmpplayername[:10] # 限制玩家机签长度
                        screen.blit(screenshot, (0, 0))
                        screen.blit(endmask, (30, 20))
                        mymenu.optiongroup.update()
                        mymenu.optiongroup.draw(screen)
                        pygame.display.flip()
                    if save: # 如果刚刚在屎山循环里选择了保存
                        replay_gzip = gzip.compress(json.dumps(jsondict).encode())
                        with gzip.open('./replay/thxxx_'+ str(slot).zfill(2) +'.rpy', 'wb') as file:
                            file.write(replay_gzip)
                        mymenu = reload() # 重载录像菜单

                if event.key == pygame.K_x:
                    se.play("cancel")
                    return
        screen.blit(screenshot, (0, 0))
        screen.blit(endmask, (30, 20))
        mymenu.optiongroup.update()
        mymenu.optiongroup.draw(screen)
        pygame.display.flip()

def gameend(playreplay):
    screenshot = screen.copy()
    endmask = pygame.Surface((590, 675))
    endmask.set_alpha(128)
    if not playreplay:
        endmask.fill("RED")
        mymenu = asset.Menu(gameui.font_24,
                            [
                                asset.MenuStruct("满身疮痍！", True),
                                asset.MenuStruct("保存录像并退出"),
                                asset.MenuStruct("不保存录像并退出")
                            ], "WHITE", "RED", "GREY", (250, 250), iscirculute=True)
    else:
        mymenu = asset.Menu(gameui.font_24,
                            [
                                asset.MenuStruct("录像播放结束！", True),
                                asset.MenuStruct("结束录像播放")
                            ], "WHITE", "RED", "GREY", (250, 250), iscirculute=True)
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    se.play("select")
                    mymenu.up()
                if event.key == pygame.K_DOWN:
                    se.play("select")
                    mymenu.down()
                if event.key == pygame.K_z:
                    se.play("confirm")
                    choice = mymenu.choose()
                    return choice,screenshot,endmask
                if event.key == pygame.K_x or event.key == pygame.K_ESCAPE:
                    return 0
        screen.blit(screenshot, (0, 0))
        screen.blit(endmask, (30, 20))
        mymenu.optiongroup.update()
        mymenu.optiongroup.draw(screen)
        pygame.display.flip()

def pause(playreplay):
    se.play("pause")
    screenshot = screen.copy()
    pausemask = pygame.Surface((590, 675))
    pausemask.set_alpha(128)
    if not playreplay:
        mymenu = asset.Menu(gameui.font_24,
                            [
                                asset.MenuStruct("游戏暂停！", True),
                                asset.MenuStruct("解除游戏暂停"),
                                asset.MenuStruct("保存录像并退出"),
                                asset.MenuStruct("不保存录像并退出")
                            ], "WHITE", "RED", "GREY", (250, 250),iscirculute=True)
    else:
        mymenu = asset.Menu(gameui.font_24,
                            [
                                asset.MenuStruct("游戏暂停！", True),
                                asset.MenuStruct("解除游戏暂停"),
                                asset.MenuStruct("结束录像播放")
                            ], "WHITE", "RED", "GREY", (250, 250), iscirculute=True)
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    se.play("select")
                    mymenu.up()
                if event.key == pygame.K_DOWN:
                    se.play("select")
                    mymenu.down()
                if event.key == pygame.K_z:
                    se.play("confirm")
                    return mymenu.choose(),screenshot,pausemask
                if event.key == pygame.K_x or event.key == pygame.K_ESCAPE:
                    return 0,screenshot,pausemask
        screen.blit(screenshot, (0, 0))
        screen.blit(pausemask, (30, 20))
        mymenu.optiongroup.update()
        mymenu.optiongroup.draw(screen)
        pygame.display.flip()

def gameloop(playreplay = False):
    done = False
    tick = 0
    input_event_list = []
    replayeventcount = 0
    tps = 60
    coldmask = pygame.Surface([590,675])
    coldmask.fill((0,64,255))
    while not done:
        clock.tick(tps)
        tick += 1
        for item in disappear_group: # 屎山之一 控制disappear分组
            if item.nowdisappeartime <= 0:
                item.kill()
                continue
            nowalpha = 255 / item.disappeartime * item.nowdisappeartime
            item.image.set_alpha(nowalpha)
            if nowalpha < 64 and hasattr(item,"isfreezebullet"):
                item.mask.clear()
            item.nowdisappeartime -= 1

        if not playreplay:
            input_event_list.append([])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        choice,screenshot,endmask = pause(playreplay)
                        if choice == 2:
                            done = True
                            replay = True
                        if choice == 3:
                            done = True
                            replay = False
                    characterctl.keydown(event.key)
                    input_event_list[tick - 1].append(
                        {"t": tick, "type": event.type, "key": event.key})
                elif event.type == pygame.KEYUP:
                    characterctl.keyup(event.key)
                    input_event_list[tick - 1].append(
                        {"t": tick, "type": event.type, "key": event.key})
                if player_Character.HP < 0:
                    done = True
                    choice,screenshot,endmask = gameend(playreplay)
                    replay = True if choice == 1 else False
        else:  # 播放录像
            nexteventtick = jsondict["replaybody"]["tick"][replayeventcount]
            if nexteventtick == tick:
                replayeventcount += 1
                if replayeventcount == len(jsondict["replaybody"]["tick"]) - 1:
                    gameend(playreplay)
                    return
                for i, eventtype in enumerate(jsondict["replaybody"]["type"][replayeventcount - 1]):
                    if eventtype == pygame.KEYDOWN:
                        characterctl.keydown(
                            jsondict["replaybody"]["key"][replayeventcount - 1][i])
                    elif eventtype == pygame.KEYUP:
                        characterctl.keyup(
                            jsondict["replaybody"]["key"][replayeventcount - 1][i])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        choice = pause(playreplay)[0]
                        if choice == 2:return
                    if event.key == pygame.K_LCTRL:
                        tps = 360 # ctrl加速录像播放
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LCTRL:
                        tps = 60
        player_Character.update(choosecharacter)
        player_CharacterImage.update()
        player_CharacterOptionLeft.update()
        player_CharacterOptionRight.update()
        enemyGroup.update()
        enemyBulletGroup.update()
        selfBulletGroup.update()
        bombgroup.update()
        effectgroup.update()
        itemGroup.update()
        if tick % 2 or not settings["powersave"]:
            gameui.drawBefore(screen)
            self_group.draw(screen)
            enemyGroup.draw(screen)
            selfBulletGroup.draw(screen)
            enemyBulletGroup.draw(screen)
            bombgroup.draw(screen)
            effectgroup.draw(screen)
            itemGroup.draw(screen)
            gameui.drawAfter(screen, baka, player_Character, se,
                             clock, score)
            if player_Character.temperature<20000: # 寒冷特效遮罩
                coldmask.set_alpha((20000-player_Character.temperature)/200)
                screen.blit(coldmask,(gameZoneLeft,gameZoneUp))
            pygame.display.flip()
    if replay: # 如果选择保存录像
        input_event_list = [x for x in input_event_list if x != []]  # 清除所有空项
        new_input_event_list = []
        type_replace_dict = {"768": "0", "769": "1"}
        key_replace_dict = {"1073741906": "0", "1073741905": "1", "1073741904": "2",
                            "1073741903": "3", "122": "4", "120": "5", "1073742049": "6", "99": "7"}
        for sublist in input_event_list:  # 将原始数据通过自定义字典转化为自定义数据
            tmpsublist = []
            for item in sublist:
                type_value = str(item["type"])
                key_value = str(item["key"])
                if not key_value in key_replace_dict:  # 如果这个键不需要被记录就跳过
                    continue
                item["key"] = key_replace_dict[key_value]
                item["type"] = type_replace_dict[type_value]
                tmpsublist.append(item)
            new_input_event_list.append(tmpsublist)  # 加入新的列表中
        new_input_event_list = [
            x for x in new_input_event_list if x != []]  # 清除所有空项
        for eachtick in new_input_event_list:  # 遍历原始数据中的每一tick
            jsondict["replaybody"]["tick"].append(eachtick[0]["t"])  # 写入tick号
            tmpkeylist = []  # 对每一tick初始化空的事件和按键列表
            tmptypelist = []
            for eachevent in eachtick:  # 遍历每一tick下的每一事件
                tmpkeylist.append(eachevent["key"])
                tmptypelist.append(eachevent["type"])
            jsondict["replaybody"]["key"].append(tmpkeylist)
            jsondict["replaybody"]["type"].append(tmptypelist)
        jsondict["metadata"]["avgfps"] = sum(
            gameui.fpslist)/len(gameui.fpslist)
        gameui.fpslist = [] # 清空帧率记录数组
        jsondict["metadata"]["score"] = score
        savereplay(screenshot,endmask)

def option():
    done = False
    global settings
    mymenu = asset.Menu(gameui.font_24,
                        [
                            asset.MenuStruct("SE Volume: {0:.0f}%".format(
                                settings["sevol"]*100)),
                            asset.MenuStruct("BGM Volume: {0:.0f}%".format(
                                settings["bgmvol"]*100)),
                            asset.MenuStruct("目标帧率: {0} FPS".format(
                                "30" if settings["powersave"] else "60")),
                            asset.MenuStruct("Save & Exit")
                        ], "BLACK", "RED", "GREY", (350, 250), iscirculute=True)
    tmpsetting = settings.copy()  # 暂存现有设置
    while not done:
        clock.tick(60)
        mainbgdraw()
        if mymenu.choose() == 0 and not pygame.mixer.Channel(se.VOLUME_TEST_CHANNEL).get_busy():
            se.play("miss", se.VOLUME_TEST_CHANNEL)  # 循环播放测试音
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    se.play("select")
                    mymenu.up()
                if event.key == pygame.K_DOWN:
                    se.play("select")
                    mymenu.down()
                if event.key == pygame.K_LEFT:
                    if mymenu.choose() == 0:
                        settings["sevol"] = max(settings["sevol"] - 0.05, 0)
                        se.soundasset["test"].set_volume(settings["sevol"])
                        mymenu.getelementbyid(0).settext(
                            "SE Volume: {0:.0f}%".format(settings["sevol"]*100))  # 完全不规范的面向对象编程
                    if mymenu.choose() == 1:
                        settings["bgmvol"] = max(settings["bgmvol"] - 0.05, 0)
                        mymenu.getelementbyid(1).settext(
                            "BGM Volume: {0:.0f}%".format(settings["bgmvol"]*100))
                    if mymenu.choose() == 2:
                        settings["powersave"] = not settings["powersave"]
                        mymenu.getelementbyid(2).settext("目标帧率: {0} FPS".format(
                            "30" if settings["powersave"] else "60"))
                if event.key == pygame.K_RIGHT:
                    if mymenu.choose() == 0:
                        settings["sevol"] = min(settings["sevol"] + 0.05, 1)
                        se.soundasset["test"].set_volume(settings["sevol"])
                        mymenu.getelementbyid(0).settext(
                            "SE Volume: {0:.0f}%".format(settings["sevol"]*100))
                    if mymenu.choose() == 1:
                        settings["bgmvol"] = min(settings["bgmvol"] + 0.05, 1)
                        mymenu.getelementbyid(1).settext(
                            "BGM Volume: {0:.0f}%".format(settings["bgmvol"]*100))
                    if mymenu.choose() == 2:
                        settings["powersave"] = not settings["powersave"]
                        mymenu.getelementbyid(2).settext("目标帧率: {0} FPS".format(
                            "30" if settings["powersave"] else "60"))
                if event.key == pygame.K_z and mymenu.choose() == 3:
                    se.setvolume(settings["sevol"])  # 应用设置
                    gameui.updatesettings(settings)
                    with open("settings.json", "w") as file:
                        file.write(json.dumps(settings))
                        return
                if event.key == pygame.K_x:  # 丢弃设置
                    se.play("cancel")
                    settings = tmpsetting.copy()
                    return
        mymenu.optiongroup.update()
        mymenu.optiongroup.draw(screen)
        pygame.display.flip()

def replay():
    global jsondict
    jsondictlist = loadreplaydata()
    menustructlist = [asset.MenuStruct("NO." + str(i).zfill(2),True) for i in range(26)] # 菜单第一项存放表头
    menustructlist[0] = asset.MenuStruct("NO.XX" + "   " + "     TIME     " + "   "+ "PLAYERNAME"  + " CHARACTER  " + "  SCORE    " + "   " + "PLR ",True)
    for i,e in enumerate(jsondictlist):
        if not jsondictlist[i]: # 第一项用来放表头了
            menustructlist[i+1] = asset.MenuStruct("NO." + str(i+1).zfill(2) + "   " + "--/--/-- --:--" + "   "+ "----------" + "   " + "------" + "   " + "----------" + "   " + "---%",True)
            continue
        menustructlist[i+1] = asset.MenuStruct("NO." + str(i+1).zfill(2) + "   " + time.strftime("%y/%m/%d %H:%M", time.localtime(e["metadata"]["time"])) + "   "+ e["metadata"]["playername"].ljust(10) + "   " + e["metadata"]["character"].ljust(6) + "   " + str(e["metadata"]["score"]).zfill(10)+ "   " + "{0:.1f}%".format((1 - min(1,e["metadata"]["avgfps"]/60))*100))
        if i==25:break
    mymenu = asset.Menu(gameui.font_mono_20,menustructlist, (20,20,20), "RED", (60,60,60), (100, 100),linesep=-5)
    titleENG = LimitTimePic(gameui.font_36.render("Replay Select",True,"WHITE"),(130,50)) # repetition good
    titleENGS = LimitTimePic(gameui.font_36.render("Replay Select",True,"BLACK"),(128,48))
    titleZHS = LimitTimePic(gameui.font_24.render("选择一份录像",True,"GREY"),(130,85))
    titleZHSS = LimitTimePic(gameui.font_24.render("选择一份录像",True,"BLACK"),(128,83))
    mymenu.optiongroup.add(titleENGS,titleENG,titleZHSS,titleZHS)
    if len(mymenu.choiceablelist):
        mymenu.down()
    while True:
        mainbgdraw()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if len(mymenu.choiceablelist) == 0: 
                        se.play("invalid")
                        continue # 录像列表为空防止报错
                    se.play("select")
                    mymenu.up()
                if event.key == pygame.K_DOWN:
                    if len(mymenu.choiceablelist) == 0: 
                        se.play("invalid")
                        continue
                    se.play("select")
                    mymenu.down()
                if event.key == pygame.K_z:
                    if len(mymenu.choiceablelist) == 0: 
                        se.play("invalid")
                        continue
                    se.play("select")
                    # 将自定义格式转换为pygame事件和按键编号
                    type_replace_dict = {"0": 768, "1": 769}
                    key_replace_dict = {"0": 1073741906, "1": 1073741905, "2": 1073741904,
                                        "3": 1073741903, "4": 122, "5": 120, "6": 1073742049, "7": 99}
                    jsondict = json.loads(json.dumps(jsondictlist[mymenu.choose() - 1])) # 我恨浅拷贝  用json迫真实现深拷贝
                    for eachtypelist in jsondict["replaybody"]["type"]:
                        for i, eachtype in enumerate(eachtypelist):
                            eachtypelist[i] = type_replace_dict[eachtype]
                    for eachkeylist in jsondict["replaybody"]["key"]:
                        for i, eachkey in enumerate(eachkeylist):
                            eachkeylist[i] = key_replace_dict[eachkey]
                    reset(True)
                    gameloop(True)
                if event.key == pygame.K_x:
                    se.play("cancel")
                    return
        mymenu.optiongroup.update()
        mymenu.optiongroup.draw(screen)
        pygame.display.flip()

def showmanual(page,readmask):
    def reloadmanualcontent(page):
        pagesurface = pygame.Surface([960,720])
        pagesurface.fill("GREY")
        pagesurface.set_colorkey("GREY")
        for i,sentence in enumerate(asset.ManualContent.textlist[page]):
            pagesurface.blit(gameui.font_24.render(sentence.text,True,"BLACK"),(99,29+40*i))
            pagesurface.blit(gameui.font_24.render(sentence.text,True,sentence.color),(100,30+40*i))
        return pagesurface
    drawgroup = pygame.sprite.Group()
    pageeffect1 = PictureAppearEffect(reloadmanualcontent(page),V2(0,20),V2(50,100),False,V2(0,360),"appearing")
    pageeffect2 = PictureAppearEffect(reloadmanualcontent(page),V2(0,20),V2(50,100),False,V2(0,360),"disappeared")
    titleENG = LimitTimePic(gameui.font_36.render("Manual",True,"WHITE"),(130,50)) # repetition good
    titleENGS = LimitTimePic(gameui.font_36.render("Manual",True,"BLACK"),(128,48))
    titleZHS = LimitTimePic(gameui.font_24.render("游戏使用说明书",True,"GREY"),(130,85))
    titleZHSS = LimitTimePic(gameui.font_24.render("游戏使用说明书",True,"BLACK"),(128,83))
    drawgroup.add(titleENGS,titleENG,titleZHSS,titleZHS,pageeffect1,pageeffect2)
    nowpagebuffer = True
    while True:
        mainbgdraw()
        screen.blit(readmask,(0,0))
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    se.play("select")
                    if page == 0: continue
                    page -= 1
                    if nowpagebuffer:
                        pageeffect1.reverse = False
                        pageeffect2.reverse = False
                        pageeffect2.image = reloadmanualcontent(page)
                        pageeffect1.disappear()
                        pageeffect2.appear()
                    else:
                        pageeffect1.reverse = False
                        pageeffect2.reverse = False
                        pageeffect1.image = reloadmanualcontent(page)
                        pageeffect1.appear()
                        pageeffect2.disappear()
                    nowpagebuffer = not nowpagebuffer
                if event.key == pygame.K_DOWN:
                    se.play("select")
                    if page == len(asset.ManualContent.textlist)-1: continue
                    page += 1
                    if nowpagebuffer:
                        pageeffect1.reverse = True
                        pageeffect2.reverse = True
                        pageeffect2.image = reloadmanualcontent(page)
                        pageeffect1.disappear()
                        pageeffect2.appear()
                    else:
                        pageeffect1.reverse = True
                        pageeffect2.reverse = True
                        pageeffect1.image = reloadmanualcontent(page)
                        pageeffect1.appear()
                        pageeffect2.disappear()
                    nowpagebuffer = not nowpagebuffer
                if event.key == pygame.K_z:
                    se.play("confirm")
                if event.key == pygame.K_x or event.key == pygame.K_ESCAPE:
                    return page
        drawgroup.update()
        drawgroup.draw(screen)
        pygame.display.flip()

def manual():
    mymenu = asset.Menu(gameui.font_36,
                    [
                        asset.MenuStruct("1.游戏的简要介绍"),
                        asset.MenuStruct("2.操作方法"),
                        asset.MenuStruct("3.游戏界面"),
                        asset.MenuStruct("4.小心低温！")
                    ], "WHITE", "RED", "GREY", (350, 250), iscirculute=True,linesep=15)
    titleENG = LimitTimePic(gameui.font_36.render("Manual",True,"WHITE"),(130,50)) # repetition good
    titleENGS = LimitTimePic(gameui.font_36.render("Manual",True,"BLACK"),(128,48))
    titleZHS = LimitTimePic(gameui.font_24.render("游戏使用说明书",True,"GREY"),(130,85))
    titleZHSS = LimitTimePic(gameui.font_24.render("游戏使用说明书",True,"BLACK"),(128,83))
    mymenu.optiongroup.add(titleENGS,titleENG,titleZHSS,titleZHS)
    readmask = pygame.Surface([960,720])
    readmask.fill("BLACK")
    readmask.set_alpha(96)
    while True:
        mainbgdraw()
        screen.blit(readmask,(0,0))
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    se.play("select")
                    mymenu.up()
                if event.key == pygame.K_DOWN:
                    se.play("select")
                    mymenu.down()
                if event.key == pygame.K_z:
                    se.play("confirm")
                    mymenu.jumpto(showmanual(mymenu.choose(),readmask))
                if event.key == pygame.K_x or event.key == pygame.K_ESCAPE:
                    return
        mymenu.optiongroup.update()
        mymenu.optiongroup.draw(screen)
        pygame.display.flip()

def showplayerdata():
    drawgroup = pygame.sprite.Group()
    charactertitlepiclist = [gameui.font_28.render("博丽灵梦",True,"RED"),gameui.font_28.render("雾雨魔理沙",True,"YELLOW")]
    charactertitle = LimitTimePic(charactertitlepiclist[0],(480,100))
    datalist = [{"playername":"----------","score":"------","time":"--/--/-- --:--:--"} for i in range(20)]
    characterdatalist = [json.loads(json.dumps(datalist)),json.loads(json.dumps(datalist))] # 前灵梦后魔理沙 迫真深拷贝
    for i,seq in playerdata["reimu"][:20]:
        characterdatalist[0][i] = seq.copy()
        seq.time = time.strftime("%y/%m/%d", time.localtime(seq.time))
    for i,seq in playerdata["marisa"][:20]:
        characterdatalist[1][i] = seq.copy()
        seq.time = time.strftime("%y/%m/%d", time.localtime(seq.time))
    nowcharacter = False # 假灵梦真魔理沙 尝试船新低可读性写法
    titleENG = LimitTimePic(gameui.font_36.render("PlayerData",True,"WHITE"),(130,50)) # repetition good
    titleENGS = LimitTimePic(gameui.font_36.render("PlayerData",True,"BLACK"),(128,48))
    titleZHS = LimitTimePic(gameui.font_24.render("查看历史记录",True,"GREY"),(130,85))
    titleZHSS = LimitTimePic(gameui.font_24.render("查看历史记录",True,"BLACK"),(128,83))
    datapanel = LimitTimePic(pygame.Surface([960,500]),(480,300))
    datapanel.image.fill("GREY")
    datapanel.image.set_colorkey("GREY")
    drawgroup.add(charactertitle,titleENGS,titleENG,titleZHSS,titleZHS,datapanel)
    for i,seq in enumerate(characterdatalist[nowcharacter]):
            datapanel.image.blit(gameui.font_mono_20.render(seq["playername"]+"     "+seq["score"]+"     "+seq["time"],True,"BLACK"),(200,150+20*i)) 

    while True:
        mainbgdraw()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    se.play("select")
                    nowcharacter = not nowcharacter
                    charactertitle.setimage(charactertitlepiclist[nowcharacter])
                    datapanel.image.fill("GREY")

                    for i,seq in enumerate(characterdatalist[nowcharacter]):
                        datapanel.image.blit(gameui.font_mono_20.render(seq["playername"]+"     "+seq["score"]+"     "+seq["time"],True,"BLACK"),(200,150+20*i)) 
                if event.key == pygame.K_x or event.key == pygame.K_ESCAPE:
                    se.play("cancel")
                    return
        drawgroup.update()
        drawgroup.draw(screen)
        pygame.display.flip()
try:
    with open('settings.json') as f:
        try:
            settings = json.load(f, strict=False)
        except json.JSONDecodeError:
            raise FileNotFoundError
except FileNotFoundError:
    settings = create_setting()

 

try:
    with gzip.open("./player.dat", 'rb') as f:
        try:
            playerdata=json.loads(gzip.decompress(
                f.read()).decode(), strict=False)
        except json.JSONDecodeError:
            raise FileNotFoundError
except FileNotFoundError:
    playerdata = create_playerdata()

score = 0
screenX = 960
screenY = 720
gameZoneLeft = 30
gameZoneRight = 620
gameZoneUp = 20
gameZoneDown = 695
gameZoneCenterX = (gameZoneLeft + gameZoneRight) / 2
gameZoneCenterY = (gameZoneUp + gameZoneDown) / 2
size = (screenX, screenY)
screen = pygame.display.set_mode(size)
gameui = asset.GameUI(settings)
se = asset.SEPlayer()
clock = pygame.time.Clock()
choosecharacter = "Reimu"
mainbgposy = 0
mainbgspeedy = 0
tick = 0
mymenu = asset.Menu(gameui.font_24, [
    asset.MenuStruct("START"), 
    asset.MenuStruct("PRACTISE START",True), 
    asset.MenuStruct("PLAYER DATA"),
    asset.MenuStruct("REPLAY"),
    asset.MenuStruct("MANUAL"),
    asset.MenuStruct("OPTION"), 
    asset.MenuStruct("MUSIC ROOM", True), 
    asset.MenuStruct("EXIT")
    ], "WHITE", "RED", "GREY", (100, 400), iscirculute=True)
while True:
    mainbgdraw()
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                se.play("select")
                mymenu.up()
            if event.key == pygame.K_DOWN:
                se.play("select")
                mymenu.down()
            if event.key == pygame.K_z:
                se.play("confirm")
                id = mymenu.choose()
                if id == 0:
                    mainbgspeedy = -20
                    charactermenu()
                    mainbgspeedy = 20
                    continue
                if id == 2:
                    showplayerdata()
                if id == 3:
                    replay()
                    continue
                if id == 4:
                    manual()
                if id == 5:
                    option()
                if id == 7:
                    pygame.time.wait(200)  # 等待音效播放完成
                    exit()
    mymenu.optiongroup.update()
    mymenu.optiongroup.draw(screen)
    pygame.display.flip()
