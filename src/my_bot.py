import traceback
from abc import ABC
from typing import List

import lugo4py
from settings import get_my_expected_position, Point, has_other_closest


class MyBot(lugo4py.Bot, ABC):
    def on_disputing(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            ball_position = inspector.get_ball().position
            me = inspector.get_me()

            if not has_other_closest(inspector, me):
                move_order = inspector.make_order_move_max_speed(ball_position)
            else:
                move_order = inspector.make_order_move_max_speed(me.position)
            catch_order = inspector.make_order_catch()
            return [move_order, catch_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def on_defending(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:

            ball_position = inspector.get_ball().position

            move_order = inspector.make_order_move_max_speed(ball_position)
            # we can ALWAYS try to catch the ball
            catch_order = inspector.make_order_catch()

            return [move_order, catch_order]
        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def on_holding(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:

            # "point" is an X and Y raw coordinate referenced by the field, so the side of the field matters!
            # "region" is a mapped area of the field create by your mapper! so the side of the field DO NOT matter!
            opponent_goal_point = self.mapper.get_attack_goal()
            goal_region = self.mapper.get_region_from_point(opponent_goal_point.get_center())
            my_region = self.mapper.get_region_from_point(inspector.get_me().position)

            if self.is_near(my_region, goal_region):
                my_order = inspector.make_order_kick_max_speed(opponent_goal_point.get_center())
            else:
                my_order = inspector.make_order_move_max_speed(opponent_goal_point.get_center())

            return [my_order]

        except Exception as e:
            print(f'did not play this turn due to exception. {e}')
            traceback.print_exc()

    def on_supporting(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            ball_holder_position = inspector.get_ball().position

            # "point" is an X and Y raw coordinate referenced by the field, so the side of the field matters!
            # "region" is a mapped area of the field create by your mapper! so the side of the field DO NOT matter!
            ball_holder_region = self.mapper.get_region_from_point(ball_holder_position)
            my_region = self.mapper.get_region_from_point(inspector.get_me().position)

            if self.is_near(ball_holder_region, my_region):
                move_dest = ball_holder_position
            else:
                move_dest = get_my_expected_position(inspector, self.mapper, self.number)

            move_order = inspector.make_order_move_max_speed(move_dest)
            return [move_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()


    def as_goalkeeper(self, inspector: lugo4py.GameSnapshotInspector, state: lugo4py.PLAYER_STATE) -> List[lugo4py.Order]:
        try:
            order_list = []
            ball_position = inspector.get_ball().position
            me = inspector.get_me()

            if state == lugo4py.PLAYER_STATE.DEFENDING:
                position = ball_position
            elif state == lugo4py.PLAYER_STATE.HOLDING_THE_BALL and inspector.is_ball_holder:
                position = self.mapper.get_attack_goal().get_center()
            else:
                position = ball_position



            if ball_position.x <= 1300 and ((ball_position.y - me.position.y) > 2000):
                move_order = inspector.make_order_jump(position, 200)
            else:
                if position.y > self.mapper.get_defense_goal().get_top_pole().y:
                    position = Point(0, 5600)
                elif position.y < self.mapper.get_defense_goal().get_bottom_pole().y:
                    position = Point(0, 4400)

                move_order = inspector.make_order_jump(position, 200)

            order_list.append(move_order)
            order_list.append(inspector.make_order_catch())


            return order_list


        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def getting_ready(self, snapshot: lugo4py.GameSnapshot):
        print('getting ready')

    def is_near(self, region_origin: lugo4py.mapper.Region, dest_origin: lugo4py.mapper.Region) -> bool:
        max_distance = 2
        return abs(region_origin.get_row() - dest_origin.get_row()) <= max_distance and abs(
            region_origin.get_col() - dest_origin.get_col()) <= max_distance