from time import time, localtime, strftime
import logging
import json
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
import bet365


api_key = ""
port = 8066

current_account, current_password = "", ""

logging.basicConfig(filename="bet365_if_yy_" + strftime("%Y-%m-%d", localtime(time())) + ".log",
                    format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s", level=logging.INFO, filemode='a', datefmt='%Y-%m-%d %H:%M:%S')

bet365.init()


def clean_team_name(name):
    n = []
    s = False
    for i in name:
        o = ord(i)
        if not s and o > 255:
            s = True
        elif s and o <= 255:
            break
        n.append(i)
    return "".join(n)


def application(environ, start_response):
    global current_account, current_password

    start_response('200 OK', [('Content-Type', 'application/json')])
    d = parse_qs(environ['QUERY_STRING'])

    request_body = {}
    for key in d:
        request_body[key] = d.get(key)[0]

    logging.info("got a instruction: %s" % (request_body, ))

    action = request_body.get("action")
    key = request_body.get("key")

    if key != api_key:
        return [json.dumps({"error": "invalid key"}).encode("utf-8")]

    if action == "login":
        account_name = request_body.get("account_name")
        account_pass = request_body.get("account_pass")

        current_account, current_password = account_name, account_pass

        r = bet365.check_login(account_name)
        if r.get("result"):
            logging.info("result: %s", (r, ))
            return [json.dumps(r).encode("utf-8")]
        else:
            bet365.login(account_name, account_pass)
            r = bet365.check_login(account_name)
            logging.info("result: %s", (r, ))
            return [json.dumps(r).encode("utf-8")]
    elif action == "check":
        r = bet365.check_login(current_account)
        if not r.get("result"):
            if current_account == "":
                logging.info("error: not login.")
                return [json.dumps({"error": "not login"}).encode("utf-8")]

            bet365.login(current_account, current_password)
            r = bet365.check_login(current_account)

        logging.info("result: %s", (r, ))
        return [json.dumps(r).encode("utf-8")]
    elif action == "find":
        if not bet365.check_login(current_account).get("result"):
            if current_account == "":
                logging.info("error: not login.")
                return [json.dumps({"error": "not login"}).encode("utf-8")]

            bet365.login(current_account, current_password)

        team_home = clean_team_name(request_body.get("team_home"))
        team_away = clean_team_name(request_body.get("team_away"))
        handicap = request_body.get("handicap")

        if handicap != None:
            handicap = float(handicap)

        r = bet365.find_game(team_home, team_away, handicap)

        logging.info("result: %s" % (r, ))
        return [json.dumps(r).encode("utf-8")]
    elif action == "bet":
        if not bet365.check_login(current_account).get("result"):
            if current_account == "":
                logging.info("error: not login.")
                return [json.dumps({"error": "not login"}).encode("utf-8")]

            bet365.login(current_account, current_password)

        team_home = clean_team_name(request_body.get("team_home"))
        team_away = clean_team_name(request_body.get("team_away"))
        handicap = request_body.get("handicap")
        team = request_body.get("team")
        money = request_body.get("money")

        if handicap != None:
            handicap = float(handicap)

        r = bet365.bet_game(team_home, team_away, handicap, team, money)

        logging.info("result: %s" % (r, ))
        return [json.dumps(r).encode("utf-8")]
    elif action == "query":
        if not bet365.check_login(current_account).get("result"):
            if current_account == "":
                logging.info("error: not login.")
                return [json.dumps({"error": "not login"}).encode("utf-8")]

            bet365.login(current_account, current_password)

        team_home = clean_team_name(request_body.get("team_home"))
        team_away = clean_team_name(request_body.get("team_away"))
        bet_date = request_body.get("bet_date")

        r = bet365.query_bet_result(team_home, team_away, bet_date)

        logging.info("result: %s" % (r, ))
        return [json.dumps(r).encode("utf-8")]

    logging.info("error: invalid command.")
    return [json.dumps({"error": "invalid command"}).encode("utf-8")]


httpd = make_server("0.0.0.0", port, application)
logging.info("serving http on port %d..." % port)
httpd.serve_forever()
