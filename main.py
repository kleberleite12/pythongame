import pygame
import random
import sys
import os

pygame.init()

# -------------------- CONFIG --------------------
LARGURA_TELA = 400
ALTURA_TELA = 600
FPS = 60

TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Flappy Ball ⚽")
RELOGIO = pygame.time.Clock()

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)

# -------------------- SONS --------------------
SOM_GAMEOVER = pygame.mixer.Sound("gameover.ogg")
SOM_GAMEOVER.set_volume(0.7)  # volume de 0.0 a 1.0

def tocar_musica(caminho, volume=0.5, loop=-1):
    pygame.mixer.music.load(caminho)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loop)

# -------------------- FONTES --------------------
def fonte(tam, negrito=False):
    return pygame.font.SysFont("Arial", tam, bold=negrito)

# -------------------- RECORDES --------------------
def carregar_recorde():
    if os.path.exists("highscore.txt"):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

def salvar_recorde(valor):
    with open("highscore.txt", "w") as f:
        f.write(str(valor))

RECORD = carregar_recorde()

# -------------------- UTIL --------------------
def carregar_imagem(caminho, tamanho=None, alpha=True, fallback_cor=(60, 160, 60)):
    """
    Carrega uma imagem. Se alpha=True, considera transparência.
    Retorna a imagem e a máscara pronta (para colisão).
    """
    try:
        img = pygame.image.load(caminho).convert_alpha() if alpha else pygame.image.load(caminho).convert()
        if tamanho:
            img = pygame.transform.smoothscale(img, tamanho)
        mask = pygame.mask.from_surface(img)
        return img, mask
    except Exception:
        surf = pygame.Surface(tamanho if tamanho else (100, 100), pygame.SRCALPHA if alpha else 0)
        surf.fill(fallback_cor)
        mask = pygame.mask.from_surface(surf)
        return surf, mask

def wrap_text(texto, fnt, max_largura):
    palavras = texto.split(" ")
    linhas, atual = [], ""
    for p in palavras:
        teste = (atual + " " + p).strip()
        if fnt.size(teste)[0] <= max_largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas

def desenhar_multilinhas_centralizado(linhas, fnt, cor, espacamento=10):
    superficies = [fnt.render(l, True, cor) for l in linhas]
    altura_total = sum(s.get_height() for s in superficies) + espacamento * (len(superficies) - 1)
    y = (ALTURA_TELA - altura_total) // 2
    for s in superficies:
        rect = s.get_rect(center=(LARGURA_TELA // 2, y + s.get_height() // 2))
        TELA.blit(s, rect)
        y += s.get_height() + espacamento

# -------------------- ASSETS --------------------
FUNDO_IMG = carregar_imagem("campodefutebol.jpg", (LARGURA_TELA, ALTURA_TELA))[0]
BOLA_IMG = carregar_imagem("ball.png", (40, 40), alpha=True)[0]
CANO_IMG, CANO_MASK = carregar_imagem("cano_cinza.png", (80, 500), alpha=True)
TELA_INICIAL = carregar_imagem("telainicial.png", (LARGURA_TELA, ALTURA_TELA))[0]

# -------------------- ENTIDADES --------------------
class Bola:
    def __init__(self):
        self.x = 50
        self.y = ALTURA_TELA // 2
        self.vel = 0
        self.gravidade = 0.6
        self.pulo = -10
        self.img = BOLA_IMG
        self.rect = self.img.get_rect(topleft=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.img)

    def update(self):
        self.vel += self.gravidade
        self.y += self.vel
        self.rect.y = int(self.y)

    def jump(self):
        self.vel = self.pulo

    def draw(self):
        TELA.blit(self.img, (self.x, int(self.y)))

class Cano:
    LARGURA = CANO_IMG.get_width()
    ALTURA = CANO_IMG.get_height()
    GAP = 150
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.altura = random.randint(120, 400)
        self.top = self.altura - Cano.ALTURA
        self.bottom = self.altura + Cano.GAP
        self.image_top = pygame.transform.flip(CANO_IMG, False, True)
        self.image_bottom = CANO_IMG
        self.rect_top = self.image_top.get_rect(topleft=(self.x, self.top))
        self.rect_bottom = self.image_bottom.get_rect(topleft=(self.x, self.bottom))
        self.mask_top = CANO_MASK
        self.mask_bottom = CANO_MASK

    def update(self):
        self.x -= Cano.VEL
        self.rect_top.x = int(self.x)
        self.rect_bottom.x = int(self.x)

    def draw(self):
        TELA.blit(self.image_top, (int(self.x), self.top))
        TELA.blit(self.image_bottom, (int(self.x), self.bottom))

    def saiu_da_tela(self):
        return self.x < -Cano.LARGURA

# -------------------- TELAS --------------------
def tela_game_over(pontos):
    global RECORD
    titulo = fonte(56, True)
    normal = fonte(24, True)
    pygame.mixer.music.stop()
    SOM_GAMEOVER.play()
    if pontos > RECORD:
        RECORD = pontos
        salvar_recorde(RECORD)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return "menu"
                if e.key == pygame.K_r:
                    return "restart"
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        TELA.blit(FUNDO_IMG, (0, 0))
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        TELA.blit(overlay, (0, 0))

        go = titulo.render("GAME OVER", True, (255, 60, 60))
        go_rect = go.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 100))
        TELA.blit(go, go_rect)

        pts = normal.render(f"Pontos: {pontos}", True, BRANCO)
        pts_rect = pts.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 40))
        TELA.blit(pts, pts_rect)

        rec = normal.render(f"Recorde: {RECORD}", True, BRANCO)
        rec_rect = rec.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2))
        TELA.blit(rec, rec_rect)

        info = normal.render("ENTER: Menu   R: Reiniciar", True, BRANCO)
        info_rect = info.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 60))
        TELA.blit(info, info_rect)

        pygame.display.flip()
        RELOGIO.tick(FPS)

def tela_instrucoes():
    f_titulo = fonte(36, True)
    f_texto = fonte(22)

    parags = [
        "INSTRUÇÕES",
        "Use ESPAÇO para fazer a bola pular.",
        "Passe entre as traves para ganhar pontos.",
        "Evite bater nos obstáculos ou no chão/teto.",
        "ESC ou ENTER para voltar ao menu."
    ]

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return "menu"

        TELA.blit(FUNDO_IMG, (0, 0))
        fade = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        fade.fill((0, 0, 0, 160))
        TELA.blit(fade, (0, 0))

        superficies = []
        for i, par in enumerate(parags):
            f = f_titulo if i == 0 else f_texto
            quebradas = wrap_text(par, f, 340) if i != 0 else [par]
            for q in quebradas:
                superficies.append((f.render(q, True, BRANCO), f))

        altura_total = sum(s.get_height() for s, _ in superficies) + 12 * (len(superficies) - 1)
        y = (ALTURA_TELA - altura_total) // 2
        for s, _ in superficies:
            r = s.get_rect(center=(LARGURA_TELA // 2, y + s.get_height() // 2))
            TELA.blit(s, r)
            y += s.get_height() + 12

        pygame.display.flip()
        RELOGIO.tick(FPS)

def tela_menu():
    global rects
    opcoes = ["Novo Jogo", "Instruções", "Sair"]
    selecionado = 0
    f_opcao = fonte(30, True)
    tocar_musica("menu.wav", 0.5, -1)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    selecionado = (selecionado - 1) % len(opcoes)
                elif e.key == pygame.K_DOWN:
                    selecionado = (selecionado + 1) % len(opcoes)
                elif e.key == pygame.K_RETURN:
                    escolha = opcoes[selecionado]
                    if escolha == "Novo Jogo":
                        return "play"
                    if escolha == "Instruções":
                        return "help"
                    if escolha == "Sair":
                        pygame.quit()
                        sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mx, my):
                        escolha = opcoes[i]
                        if escolha == "Novo Jogo":
                            return "play"
                        if escolha == "Instruções":
                            return "help"
                        if escolha == "Sair":
                            pygame.quit()
                            sys.exit()

        TELA.blit(TELA_INICIAL, (0, 0))

        rects = []
        base_y = 360
        x_esq = 60
        seta_offset = 28

        for i, txt in enumerate(opcoes):
            surf = f_opcao.render(txt, True, BRANCO)
            rect = surf.get_rect(topleft=(x_esq, base_y + i * 60))
            rects.append(rect)
            TELA.blit(surf, rect)

            if i == selecionado:
                pygame.draw.polygon(
                    TELA,
                    VERMELHO,
                    [(rect.left - seta_offset, rect.centery - 10),
                     (rect.left - seta_offset + 18, rect.centery),
                     (rect.left - seta_offset, rect.centery + 10)]
                )

        f_small = fonte(20, True)
        rec = f_small.render(f"Recorde: {RECORD}", True, BRANCO)
        TELA.blit(rec, (10, 10))

        pygame.display.flip()
        RELOGIO.tick(FPS)

# -------------------- JOGO --------------------
def jogar():
    bola = Bola()
    canos = [Cano(300)]
    pontos = 0
    f_pontos = fonte(28, True)
    tocar_musica("jogo.wav", 0.5, -1)

    while True:
        RELOGIO.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    bola.jump()
                if e.key == pygame.K_ESCAPE:
                    return "menu"

        bola.update()
        for c in canos:
            c.update()

        if canos[-1].x < LARGURA_TELA - 200:
            canos.append(Cano(LARGURA_TELA + 10))

        if canos[0].saiu_da_tela():
            canos.pop(0)
            pontos += 1

        for c in canos:
            off_top = (c.rect_top.x - bola.rect.x, c.rect_top.y - bola.rect.y)
            if bola.mask.overlap(c.mask_top, off_top):
                res = tela_game_over(pontos)
                if res == "restart":
                    return "play"
                return "menu"

            off_bottom = (c.rect_bottom.x - bola.rect.x, c.rect_bottom.y - bola.rect.y)
            if bola.mask.overlap(c.mask_bottom, off_bottom):
                res = tela_game_over(pontos)
                if res == "restart":
                    return "play"
                return "menu"

        if bola.rect.top <= 0 or bola.rect.bottom >= ALTURA_TELA:
            res = tela_game_over(pontos)
            if res == "restart":
                return "play"
            return "menu"

        TELA.blit(FUNDO_IMG, (0, 0))
        for c in canos:
            c.draw()
        bola.draw()

        placar = f_pontos.render(f"Pontos: {pontos}", True, BRANCO)
        TELA.blit(placar, (10, 10))

        f_small = fonte(22, True)
        rec = f_small.render(f"Recorde: {RECORD}", True, BRANCO)
        TELA.blit(rec, (10, 40))

        pygame.display.flip()

# -------------------- LOOP DE ESTADOS --------------------
def main():
    estado = "menu"
    while True:
        if estado == "menu":
            prox = tela_menu()
            estado = prox
        elif estado == "help":
            estado = tela_instrucoes()
        elif estado == "play":
            estado = jogar()
        else:
            estado = "menu"

if __name__ == "__main__":
    main()
