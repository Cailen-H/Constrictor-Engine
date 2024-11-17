import pygame as pg
from random import randint

flags = pg.SCALED
screen = pg.display.set_mode((1920, 1504), flags, vsync=1)
pg.init()

clock = pg.time.Clock()
pg.display.set_caption("Constrictor Engine GUI")

piscolabis_font = pg.font.Font("piscolabis-main/fonts/Piscolabis-Regular.ttf", 70)

EMPTY = 0

KING = 1
PAWN = 2
KNIGHT = 3
BISHOP = 4
ROOK = 5
QUEEN = 6


piece_imgs = {KING : pg.image.load("pieces/white_king.png"),
              PAWN : pg.image.load("pieces/white_pawn.png"),
              KNIGHT : pg.image.load("pieces/white_knight.png"),
              BISHOP : pg.image.load("pieces/white_bishop.png"),
              ROOK : pg.image.load("pieces/white_rook.png"),
              QUEEN : pg.image.load("pieces/white_queen.png"),
              KING + 6 : pg.image.load("pieces/black_king.png"),
              PAWN + 6 : pg.image.load("pieces/black_pawn.png"),
              KNIGHT + 6 : pg.image.load("pieces/black_knight.png"),
              BISHOP + 6 : pg.image.load("pieces/black_bishop.png"),
              ROOK + 6 : pg.image.load("pieces/black_rook.png"),
              QUEEN + 6 : pg.image.load("pieces/black_queen.png")}


move_opt = pg.image.load("move.png")
take_opt = pg.image.load("take.png")
debug_opt = pg.image.load("debug.png")

start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
board = []

move_sound_effects = [pg.mixer.Sound("sound_effects/Wood Block1.wav"),
                      pg.mixer.Sound("sound_effects/Wood Block2.wav"),
                      pg.mixer.Sound("sound_effects/Wood Block3.wav")]


def fen_to_board(fen):
    """ convert fen notation string to board that can be used with engine [TO BE COMPLETED] """
    board_from_fen = []
    i = 0
    rank = 0

    while (rank != 7) or (fen[i] != " "):
        # rook
        if fen[i].lower() == "r":
            board_from_fen.append(ROOK + (fen[i].islower() * 6))
        
        # knight
        elif fen[i].lower() == "n":
            board_from_fen.append(KNIGHT + (fen[i].islower() * 6))
        
        # bishop
        elif fen[i].lower() == "b":
            board_from_fen.append(BISHOP + (fen[i].islower() * 6))

        # queen        
        elif fen[i].lower() == "q":
            board_from_fen.append(QUEEN + (fen[i].islower() * 6))

        # king
        elif fen[i].lower() == "k":
            board_from_fen.append(KING + (fen[i].islower() * 6))

        # pawn
        elif fen[i].lower() == "p":
            board_from_fen.append(PAWN + (fen[i].islower() * 6))
        
        # blank squares
        elif fen[i] in [str(num) for num in range(9)]:
            for blanks in range(int(fen[i])):
                board_from_fen.append(EMPTY)

        # rank complete
        elif fen[i] == "/":
            rank += 1
        
        i += 1
    
    return board_from_fen


def board_to_fen(board):
    """ convert engine board to fen notation string. 
        board_to_fen(board : array 64) -> fen : string [TO-DO] """
    
    fen_from_board = ""

    return fen_from_board


def draw_bg(board, legal_moves, takes, drag_n_drop=[False, -1, (0, 0)]):
    """ draw squares, pieces and side bar """
    count = 1

    square = 0

    # draw squares
    for y in range(0, 1504, 188):
        count += 1
        for x in range(0, 1504, 188):
            if count % 2 == 0:
                col = (167, 117, 77)
            else:
                col = (220, 204, 187)

            pg.draw.rect(screen, col, pg.Rect(x, y, 188, 188))

            # skip piece in drag n drop state
            if (drag_n_drop[0] is True) and (drag_n_drop[1] == square):
                count += 1
                square += 1
                continue
            
            # draw piece
            if board[square] != EMPTY:
                screen.blit(piece_imgs[board[square]], (x, y))
            
            # draw move options
            if square in legal_moves:
                if takes[legal_moves.index(square)] is True:
                    screen.blit(take_opt, (x, y))
                elif takes[legal_moves.index(square)] == "debug":
                    screen.blit(debug_opt, (x, y))
                else:
                    screen.blit(move_opt, (x, y))

            count += 1
            square += 1

    
    # draw sidebar
    bg_col = (30, 30, 36)
    pg.draw.rect(screen, bg_col, pg.Rect(1504, 0, 416, 1504))

    # draw drag n drop piece
    if drag_n_drop[0] is True:
        # temporary scaled up image of piece that is being dragged
        temp_img = pg.transform.scale_by(piece_imgs[board[drag_n_drop[1]]], 1.1)


        screen.blit(temp_img, drag_n_drop[2])



def get_legal(board, index, can_castle):
    """ Given a board array and piece index return legal move indices for the piece at the index  """
    moves = []
    takes = []
    
    if board[index] == EMPTY:
        return ([], [])

    # white pawn
    elif board[index] == PAWN:
        if board[index - 8] == EMPTY:
            moves.append(index - 8)
            takes.append(False)

            if (index >= 48) and (board[index - 16] == EMPTY):
                moves.append(index - 16)
                takes.append(False)
        
        if (board[index - 7] > QUEEN) and (index % 8 != 7):
            moves.append(index - 7)
            takes.append(True)
        
        if (board[index - 9] > QUEEN) and (index % 8 != 0):
            moves.append(index - 9)
            takes.append(True)
    
    # black pawn
    elif board[index] == PAWN + 6:
        if board[index + 8] == EMPTY:
            moves.append(index + 8)
            takes.append(False)

            if (index < 16) and (board[index + 16] == EMPTY):
                moves.append(index + 16)
                takes.append(False)
            
        if ((board[index + 7] <= QUEEN) and (board[index + 7] != EMPTY)) and (index % 8 != 0):
            moves.append(index + 7)
            takes.append(True)
        
        if ((board[index + 9] <= QUEEN) and (board[index + 9] != EMPTY)) and (index % 8 != 7):
            moves.append(index + 9)
            takes.append(True)

    # white rook (plus queen horizontal/vertical)
    if (board[index] == ROOK) or (board[index] == QUEEN):
        # right
        for i in range(index + 1, (index // 8 + 1) * 8):
            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] > 6:
                moves.append(i)
                takes.append(True)
                break
            else:
                break

        # left
        for i in range(index - 1, (index // 8) * 8 - 1, -1):
            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] > 6:
                moves.append(i)
                takes.append(True)
                break
            else:
                break
        
        # up
        for i in range(index - 8, index % 8 - 1, -8):
            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] > 6:
                moves.append(i)
                takes.append(True)
                break
            else:
                break

        # down
        for i in range(index + 8, 56 + index % 8 + 1, 8):
            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] > 6:
                moves.append(i)
                takes.append(True)
                break
            else:
                break

    # black rook (plus queen horizontal/vertical)
    if (board[index] == ROOK + 6) or (board[index] == QUEEN + 6):
        # right
        for i in range(index + 1, (index // 8 + 1) * 8):
            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] <= 6:
                moves.append(i)
                takes.append(True)
                break
            else:
                break

        # left
        for i in range(index - 1, (index // 8) * 8 - 1, -1):
            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] <= 6:
                moves.append(i)
                takes.append(True)
                break
            else:
                break
        
        # up
        for i in range(index - 8, index % 8, -8):
            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] <= 6:
                moves.append(i)
                takes.append(True)
                break
            else:
                break

        # down
        for i in range(index + 8, 56 + index % 8 + 1, 8):
            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] <= 6:
                moves.append(i)
                takes.append(True)
                break
            else:
                break
    
    # white bishop (plus queen diagonals)
    if (board[index] == BISHOP) or (board[index] == QUEEN):
        # up + left
        i = index

        while ((i % 8 != 0) and (i < 64)) and (i >= 0):
            i -= 9
            if board[i] > QUEEN:
                moves.append(i)
                takes.append(True)
                break
            elif board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif i != index:
                break
        
        # up + right
        i = index
        while (i < 64) and (i >= 0): 
            if (i != index) and (i % 8 == 0):
                break
            
            if board[i] > QUEEN:
                moves.append(i)
                takes.append(True)
                break
            elif board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif i != index:
                break

            i -= 7
            

        # down + right
        i = index

        while (i < 64) and (i >= 0):
            if (i != index) and (i % 8 == 0):
                break

            if board[i] > QUEEN:
                moves.append(i)
                takes.append(True)
                break
            elif board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif i != index:
                break
            
            i += 9

        # down + left
        i = index

        while i % 8 != 0:
            i += 7

            if (i >= 64) or (i < 0):
                break

            if board[i] > QUEEN:
                moves.append(i)
                takes.append(True)
                break
            elif board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif i != index:
                break

    # black bishop (plus queen diagonals)
    if (board[index] == BISHOP + 6) or (board[index] == QUEEN + 6):
        # up + left
        i = index

        while ((i % 8 != 0) and (i < 64)) and (i >= 0):
            i -= 9
            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] <= QUEEN:
                moves.append(i)
                takes.append(True)
                break
            elif i != index:
                break
        
        # up + right
        i = index
        while (i < 64) and (i >= 0): 
            if (i != index) and (i % 8 == 0):
                break
            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] <= QUEEN:
                moves.append(i)
                takes.append(True)
                break
            elif i != index:
                break

            i -= 7
            

        # down + right
        i = index

        while (i < 64) and (i >= 0):
            if (i != index) and (i % 8 == 0):
                break
            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] <= QUEEN:
                moves.append(i)
                takes.append(True)
                break
            elif i != index:
                break
            
            i += 9

        # down + left
        i = index

        while i % 8 != 0:
            i += 7
            
            if (i >= 64) or (i < 0):
                break

            if board[i] == EMPTY:
                moves.append(i)
                takes.append(False)
            elif board[i] <= QUEEN:
                moves.append(i)
                takes.append(True)
                break
            elif i != index:
                break
    
    # white knight
    if board[index] == KNIGHT:
        possible = []

        if index % 8 < 7:
            up_right = index + 16 + 1
            down_right = index - 16 + 1

            possible.append(up_right)
            possible.append(down_right)
        
        if index % 8 >= 1:
            down_left = index - 16 - 1
            up_left = index + 16 - 1

            possible.append(down_left)
            possible.append(up_left)

        if index % 8 < 6:
            right_up = index + 8 + 2
            right_down = index - 8 + 2

            possible.append(right_up)
            possible.append(right_down)
        
        if index % 8 > 2:
            left_down = index - 8 - 2
            left_up = index + 8 - 2

            possible.append(left_down)
            possible.append(left_up)

        for move in possible:
            if (move >= 0) and (move < 64):
                if board[move] == EMPTY:
                    moves.append(move)
                    takes.append(False)
                elif board[move] > QUEEN:
                    moves.append(move)
                    takes.append(True)

    # black knight
    if board[index] == KNIGHT + 6:
        possible = []

        if index % 8 < 7:
            up_right = index + 16 + 1
            down_right = index - 16 + 1

            possible.append(up_right)
            possible.append(down_right)
        
        if index % 8 >= 1:
            down_left = index - 16 - 1
            up_left = index + 16 - 1

            possible.append(down_left)
            possible.append(up_left)

        if index % 8 < 6:
            right_up = index + 8 + 2
            right_down = index - 8 + 2

            possible.append(right_up)
            possible.append(right_down)
        
        if index % 8 > 2:
            left_down = index - 8 - 2
            left_up = index + 8 - 2

            possible.append(left_down)
            possible.append(left_up)

        for move in possible:
            if (move >= 0) and (move < 64):
                if board[move] == EMPTY:
                    moves.append(move)
                    takes.append(False)
                elif board[move] <= QUEEN:
                    moves.append(move)
                    takes.append(True)
    
    # white king
    if board[index] == KING:
        for x in range(-1, 2, 1):
            for y in range(-1, 2, 1):
                move_index = index + x + (y * 8)

                # skip square king is on
                if move_index == index:
                    continue
                
                # skip squares which are not on the same rank as the king 
                elif (move_index % 8 == 7) and (index % 8 == 0):
                    continue
                elif (move_index % 8 == 0) and (index % 8 == 7):
                    continue


                if (move_index >= 0) and (move_index < 64):
                    if board[move_index] == EMPTY:
                        moves.append(move_index)
                        takes.append(False)
                    elif board[move_index] > QUEEN:
                        moves.append(move_index)    
                        takes.append(True)
        
        # can white castle kingside ?
        if can_castle[0]:
            opp_moves = get_opponent_moves(board, 6)
            kingside = True

            # check if king side castle is legal
            for square in range(61, 63):
                if square in opp_moves:
                    kingside = False
                    
                elif board[square] != EMPTY:
                    kingside = False
            
            if kingside:
                moves.append(62)
                takes.append(False)
        
        # can white castle queenside ?
        if can_castle[1]:
            opp_moves = get_opponent_moves(board, 6)
            queenside = True

            # check if queen side castle is legal
            for square in range(57, 60):
                if square in opp_moves:
                    queenside = False
                elif board[square] != EMPTY:
                    queenside = False

            if queenside:
                moves.append(58)
                takes.append(False)
            

    # black king
    if board[index] == KING + 6:
        for x in range(-1, 2, 1):
            for y in range(-1, 2, 1):
                move_index = index + x + (y * 8)
               
                # skip square king is on
                if move_index == index:
                    continue
                
                # skip squares which are not on the same rank as the king 
                elif (move_index % 8 == 7) and (index % 8 == 0):
                    continue
                elif (move_index % 8 == 0) and (index % 8 == 7):
                    continue

                if (move_index >= 0) and (move_index < 64):
                    if board[move_index] == EMPTY:
                        moves.append(move_index)
                        takes.append(False)
                    elif board[move_index] <= QUEEN:
                        moves.append(move_index)    
                        takes.append(True)          

        # can black castle kingside ?
        if can_castle[2]:
            opp_moves = get_opponent_moves(board, 0)
            kingside = True

            # check if king side castle is legal
            for square in range(5, 7):
                if square in opp_moves:
                    kingside = False
                elif board[square] != EMPTY:
                    kingside = False
            
            if kingside:
                moves.append(6)
                takes.append(False)
    
        # can black castle queenside
        if can_castle[3]:  
            opp_moves = get_opponent_moves(board, 0)
            queenside = True

            # check if queen side castle is legal
            for square in range(1, 4):
                if square in opp_moves:
                    queenside = False
                elif board[square] != EMPTY:
                    queenside = False

            if queenside:
                moves.append(2)
                takes.append(False)

    return (moves, takes)


def get_opponent_moves(board, opponent_piece_offset):
    """ Returns a list of squares that the opponent can legally move to on the given board """    

    opp_pieces = [PAWN, KING, QUEEN, BISHOP, ROOK, KNIGHT]
    opp_pieces = [piece + opponent_piece_offset for piece in opp_pieces]

    opp_moves = []

    for b_index in range(64):
        if board[b_index] in opp_pieces:
            opp_piece_moves = get_legal(board, b_index, [False, False, False, False])[0]

            for square_index in opp_piece_moves:
                opp_moves.append(square_index)
    
    return opp_moves


def in_check(board, king_index):
    """ Checks if black or white King at specified index is currently in check """

    offset_param = 6 if (board[king_index] == KING) else 0
    opp_moves = get_opponent_moves(board, offset_param)

    if king_index in opp_moves:
        return True
    else:
        return False


def move_piece(board, moving_piece_index, to_move_to_index, piece_offset, can_castle=[True, True, True, True]):
    # [white kingside, white queenside, black kingside, black queenside]
    updated_can_castle = [b for b in can_castle]

    # check for castling and handle rook movement too
    if (board[moving_piece_index] == KING + piece_offset):
        if (abs(moving_piece_index - to_move_to_index) == 2):
            # white kingside castle
            if to_move_to_index == 62:
                board[63] = EMPTY
                board[61] = ROOK
                updated_can_castle[0] = False
            
            # white queenside castle
            elif to_move_to_index == 58:
                board[56] = EMPTY
                board[59] = ROOK
                updated_can_castle[1] = False

            # black kingside castle
            elif to_move_to_index == 6:
                board[7] = EMPTY
                board[5] = ROOK + 6
                updated_can_castle[2] = False

            # black queenside castle       
            elif to_move_to_index == 2:
                board[0] = EMPTY
                board[3] = ROOK + 6
                updated_can_castle[3] = False
        
        # regular king move (so right to castle is now gone for player who moved king)
        else:
            # white king
            if piece_offset == 0:
                updated_can_castle[0], updated_can_castle[1] = False, False
            
            # black king
            elif piece_offset == 6: 
                updated_can_castle[2], updated_can_castle[3] = False, False

    rook_squares = [63, 56, 7, 0]

    # check if player is moving a rook and lost the right to castle kingside or queenside
    if moving_piece_index in rook_squares:
        if updated_can_castle[rook_squares.index(moving_piece_index)] is True:
            updated_can_castle[rook_squares.index(moving_piece_index)] = False

    # naive move carried out
    square_copy = board[to_move_to_index]
    board[to_move_to_index] = board[moving_piece_index]
    board[moving_piece_index] = EMPTY        

    # Check if move results in check for white/black. If so reverse naive move as it is not legal.
    if in_check(board, board.index(KING + piece_offset)):
        moved_piece = board[to_move_to_index]
        board[to_move_to_index] = square_copy
        board[moving_piece_index] = moved_piece

        # naive move failed 
        return (board, False, can_castle)
    
    else:
        # can white pawn promote ?
        if (board[to_move_to_index] == PAWN) and (to_move_to_index < 8):
            board = promote_pawn_selection(board, board_index, piece_offset=0)
        
        # can black pawn promote ?
        elif (board[to_move_to_index] == PAWN + 6) and (to_move_to_index >= 56):
            board = promote_pawn_selection(board, board_index, piece_offset=6)

        # move succeeded
        return (board, True, updated_can_castle)


def promote_pawn_selection(board, board_index, piece_offset):
    choosing = True

    # promotion pieces thumbnail images
    thumbnail_codes = [QUEEN, ROOK, KNIGHT, BISHOP]
    thumbnails = [pg.transform.scale(piece_imgs[thumbnail_code + piece_offset], (94, 94)) for thumbnail_code in thumbnail_codes]

    ui_posx, ui_posy = ((board_index % 8) * 188), ((board_index // 8) * 188)

    ui_rect_surf = pg.Surface((396, 100))
    ui_rect_surf.set_alpha(8)
    ui_rect_surf.fill((199, 234, 228))

    for i, thumbnail in enumerate(thumbnails):
        ui_rect_surf.blit(thumbnail, (i * 95, 0))
    
    # ui for user to make promotion piece choice
    while choosing:
        screen.blit(ui_rect_surf, (ui_posx, ui_posy))

        pg.display.update()

        for event in pg.event.get():
            # check if user has clicked on an option
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_posx, mouse_posy = pg.mouse.get_pos()

                # in bounds of thumbnail ui ? 
                if (mouse_posx > ui_posx) and (mouse_posx < ui_posx + 396):
                    if (mouse_posy > ui_posy) and (mouse_posy < ui_posy + 100):
                        piece_option = (mouse_posx - ui_posx) // 95
                        board[board_index] = thumbnail_codes[piece_option] + piece_offset
                        choosing = False

        clock.tick()

    return board
    



board = fen_to_board(start_fen)
legal_moves = []
take_moves = []

moving = False
moving_index = 0

white_move = True

piece_drag = False
drag_n_drop_details = [False, -1, (0, 0)]

# format of [Kingside (white) : Bool, Queenside (white) : Bool, Kingside (black) : Bool, Queenside (black) : Bool]
can_castle = [True, True, True, True]


""" ====================== Main Program ====================== """

if __name__ == "__main__":
    draw_bg(board, legal_moves, take_moves)
    pg.display.update()

    while True:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()

                rank = pos[1] // 188
                file = pos[0] // 188

                board_index = rank * 8 + file

                # white's move
                if white_move is True:
                    if ((board[board_index] <= QUEEN) and not(board_index in legal_moves)):
                        legal_moves, take_moves = get_legal(board, board_index, can_castle)
                        moving_index = board_index

                        if board[board_index] != EMPTY:
                            piece_drag = True
                
                    # move piece
                    if board_index in legal_moves:
                        board, move_made, can_castle = move_piece(board, moving_index, board_index, 0, can_castle)

                        legal_moves = []
                        take_moves = []

                        if move_made:
                            white_move = False
                            piece_drag = False
                            drag_n_drop_details = [False, -1, (0, 0)]
                            move_sound_effects[randint(0, 1)].play()
                
                # black's move
                else:
                    if ((board[board_index] > QUEEN) or (board[board_index] == EMPTY)) and not(board_index in legal_moves):
                        legal_moves, take_moves = get_legal(board, board_index, can_castle)
                        moving_index = board_index
                        
                        if board[board_index] != EMPTY:
                            piece_drag = True
                
                    # move piece
                    if board_index in legal_moves:
                        board, move_made, can_castle = move_piece(board, moving_index, board_index, 6, can_castle)

                        legal_moves = []
                        take_moves = []

                        if move_made:
                            white_move = True
                            piece_drag = False
                            drag_n_drop_details = [False, -1, (0, 0)]
                            move_sound_effects[randint(0, 1)].play()
            
            # drag and drop move handling
            elif event.type == pg.MOUSEBUTTONUP:
                piece_drag = False

                pos = pg.mouse.get_pos()

                rank = pos[1] // 188
                file = pos[0] // 188

                board_index = rank * 8 + file

                # move piece
                if board_index in legal_moves:
                    if white_move:
                        piece_offset = 0
                    else:
                        piece_offset = 6

                    board, move_made, can_castle = move_piece(board, moving_index, board_index, piece_offset, can_castle)

                    legal_moves = []
                    take_moves = []

                    if move_made:
                        white_move = not(white_move)
                        move_sound_effects[randint(0, 1)].play()
                
                piece_drag = False
                drag_n_drop_details = [False, -1, (0, 0)]

            
            # close window / exit
            if event.type == pg.QUIT:
                quit()


        if piece_drag:
            positionx, positiony = pg.mouse.get_pos()
            drag_n_drop_details = [True, moving_index, (positionx - 94, positiony - 94)]
        
        draw_bg(board, legal_moves, take_moves, drag_n_drop_details)
        
        # display current move colour
        if white_move:


        
            screen.blit(piscolabis_font.render("White to move", True, (255, 90, 95)), (1570, 745))
        else:
            screen.blit(piscolabis_font.render("Black to move", True, (255, 90, 95)), (1570, 745))
        
        pg.display.update()
        
        clock.tick()
            
