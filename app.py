import base64
import os
import re
import requests

from flask import Flask
from flask import json
from flask import session
from flask import request
from flask import redirect
from flask import render_template
from flask import url_for
from flask_wtf.csrf import CSRFProtect

from urllib.parse import urljoin

from forms import PasscodeForm
from forms import SendMsgForm
from forms import SurveyForm
from forms import TestFinderForm

from helper_modules import lang_to_flag
from helper_modules import country_location
from helper_modules import translated_content
from helper_modules import decrypt

app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')
app.url_map.strict_slashes = False

csrf = CSRFProtect(app)

backend_server = app.config["BACKEND_SERVER"]
pn_services_server = app.config["PN_SERVICES_SERVER"]
button_colors = ["btn-dark-blue", "btn-burnt-orange", "btn-sea-green", "btn-dark-yellow",
                 "btn-light-blue", "btn-light-cyan", "btn-primary", "btn-success",
                 "btn-danger"]


@app.context_processor
def context_processor():
    """
    Global dict-vars visible by all templates
    """
    base_data, lang = translated_content(request, "base/base")
    base_data["risk"], lang = translated_content(request, "risk/risk")
    base_data["lang"] = lang
    base_data["acknowledgement_parts"] = base_data["policies_acknowledgements"].split("|")

    return base_data


@app.errorhandler(404)
def page_not_found(error):
    loc_data, lang = translated_content(request, "errors/errors")
    app.logger.error('Page not found: %s', (request.path))
    return render_template('404.html', loc_data=loc_data), 404


@app.errorhandler(500)
def internal_server_error(error):
    loc_data, lang = translated_content(request, "errors/errors")
    app.logger.error('Server Error: %s', (error))
    return render_template('500.html', loc_data=loc_data), 500


@app.errorhandler(Exception)
def unhandled_exception(e):
    loc_data, lang = translated_content(request, "errors/errors")
    app.logger.error('Unhandled Exception: %s', (e))
    return render_template('500.html', loc_data=loc_data), 500


@app.route("/cookies-policy")
def show_cookies_policy():
    tmp_lang = request.args.get("lang")
    lang = tmp_lang if tmp_lang in ["en", "it", "lt", "hr"] else "en"

    with open("tr/policies/Cookies_Policy_{}.html".format(lang), encoding='utf-8') as html_fp:
        loc_html = html_fp.read()

    return render_template('policies.html', loc_html=loc_html)


@app.route("/privacy-policy")
def show_privacy_policy():
    tmp_lang = request.args.get("lang")
    lang = tmp_lang if tmp_lang in ["en", "it", "lt", "hr"] else "en"

    with open("tr/policies/Privacy_Policy_{}.html".format(lang), encoding='utf-8') as html_fp:
        loc_html = html_fp.read()

    return render_template('policies.html', loc_html=loc_html)


@app.route("/")
@app.route("/index")
def index():
    # localization data for html
    loc_data, lang = translated_content(request, "index/index")

    images = ["risk2.jpg", "facts3.jpg", "tb3.png",
              "prep.png", "uequalsu.jpg", "pn2.jpg",
              "finder2.jpg", "survey_a.jpg"]

    hrefs = ["", "facts", "TBfacts", "PrEP", "UequalsU", "pn",
             "testfinder", "survey"]


    for indx, card in enumerate(loc_data["cards"]):
        card["img"] = "images/{}".format(images[indx])
        card["href"] = hrefs[indx]

    return render_template("main.html", loc_data=loc_data, lang=lang)


@app.route("/risk/<qpath>", methods = ['POST', 'GET'])
def risk(qpath=None):
    lang = request.args.get('lang') or "en"

    answer = "option_no"

    if not session.get("access_token"):
        get_url = "/".join([backend_server, "create_token"])
        response = requests.get(get_url)
        if response.status_code == 200:
            json_data = response.json()
            session["access_token"] = json_data.get("access_token")
            session["refresh_token"] = json_data.get("refresh_token")
        else:
            return render_template("500.html")

    if request.method == 'POST':
        req_data = request.form
        req_data_keys = list(req_data.keys())

        req_data_keys.remove("csrf_token")
        r_path = req_data_keys.pop() if req_data_keys else ""

        qpath = req_data["path"] if "path" in req_data else r_path

        if "path" not in req_data:
        #     _, qpath = qpath.split("/")

            # Retake test or take condom test keeping the same token
            if qpath:
                return redirect(url_for("risk", qpath=qpath, lang=lang))

            # Else "got it", go to home page
            else:
                return redirect(url_for("index", lang=lang))

        try:
            answer = next(filter(lambda x: "option_" in x, req_data.keys()))
        except StopIteration:
            pass

    post_url = urljoin(backend_server, qpath)

    headers = {"Content-Type": "application/json",
               "Accept": "application/json",
               "Authorization": "Bearer {}".format(
                   session.get("access_token", None)
               ) if session.get("access_token", None) else ""
               }

    json_params = {"language": lang} if qpath=="q1" else {"language": lang,
                                                          "answer": answer}

    response = requests.post(post_url, json=json_params, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.text)
        data["link-colors"] = ["btn-danger", "btn-dark", "btn-primary"]
        data["btn-colors"] = button_colors[:len(data["data"]["options"])]

    # If not authorized, most probably access token expired, refresh token
    elif response.status_code == 401:
        if session.get("refresh_token"):
            refresh_url = "/".join([backend_server, "refresh_token"])

            ref_headers = {"Content-Type": "application/json",
                       "Accept": "application/json",
                       "Authorization": "Bearer {}".format(
                           session.get("refresh_token", None)
                       ) if session.get("refresh_token", None) else ""
                           }

            refresh_resp = requests.get(refresh_url, headers=ref_headers)
            if refresh_resp.status_code == 200:
                refresh_json = refresh_resp.json()
                session["access_token"] = refresh_json.get("access_token")
                headers = {"Content-Type": "application/json",
                           "Accept": "application/json",
                           "Authorization": "Bearer {}".format(
                               session.get("access_token", None)
                           ) if session.get("access_token", None) else ""
                           }
                resp = requests.post(post_url, json=json_params, headers=headers)
                if resp.status_code == 200:
                    data = json.loads(resp.text)
                    data["link-colors"] = ["btn-danger", "btn-dark", "btn-primary"]
                    data["btn-colors"] = button_colors[:len(data["data"]["options"])]
                else:
                    return render_template("{}.html".format(resp.status_code))
    else:
        return render_template("{}.html".format(response.status_code))

    # elif response.status_code == 404:
    #     return render_template("404.html")
    # elif response.status_code == 405:
    #     return render_template("405.html")
    # elif response.status_code == 500:
    #     return render_template("500.html")

    return render_template("risk.html", data=data)


@app.route("/facts")
def facts():
    loc_data, lang = translated_content(request, "facts/facts")

    ids = ["HIV", "hepA", "hepB", "hepC", "chlamydia",
           "gonorrhoea", "syphilis", "LGV"]

    for indx, tab in enumerate(loc_data["tabs"]):
        tab["id"] = ids[indx]

    return render_template("facts.html", loc_data=loc_data)


@app.route("/TBfacts")
def tuberculosis():
    loc_data, lang = translated_content(request, "TB/TB")
    return render_template("TBfacts.html", loc_data=loc_data, lang=lang)


@app.route("/PrEP")
@app.route("/DoesPrEPWork")
@app.route("/IntermittentPrEP")
@app.route("/IsPrEPWorthIt")
@app.route("/PrEPWomen")
def prep():
    # Choosing template depending on path
    path_to_buttons = {"PrEP": ["DoesPrEPWork", "IsPrEPWorthIt", "IntermittentPrEP", "PrEPWomen"],
                       "DoesPrEPWork": ["PrEP", "IsPrEPWorthIt", "IntermittentPrEP", "PrEPWomen"],
                       "IntermittentPrEP": ["PrEP",  "DoesPrEPWork", "IsPrEPWorthIt", "PrEPWomen"],
                       "IsPrEPWorthIt": ["PrEP",  "DoesPrEPWork", "IntermittentPrEP", "PrEPWomen"],
                       "PrEPWomen": ["PrEP",  "DoesPrEPWork", "IsPrEPWorthIt", "IntermittentPrEP"]}
    path = request.path.strip("/")

    # Buttons for specific path
    buttons = path_to_buttons[path]
    btn_colors = ["btn-light", "btn-success", "btn-danger", "btn-warning"]

    loc_data, lang = translated_content(request, "PrEP/{}".format(path))
    all_base, _ = translated_content(request, "PrEP/PrEP_base")
    all_base["buttons"] = { btn: (all_base["buttons"][btn], btn_colors[indx]) for indx, btn in enumerate(buttons)}
    loc_data.update(all_base)

    return render_template("PrEP.html", loc_data=loc_data)


@app.route("/UequalsU")
def u_equals_u():
    loc_data, lang = translated_content(request, "UequalsU/UequalsU")
    return render_template("UequalsU.html", loc_data=loc_data)


@app.route("/testfinder")
def test_finder():
    loc_data, lang = translated_content(request, "test_finder/test_finder")

    # Retrieve countries from endpoint
    with open("virtual_endpoints/test_finder.json", encoding='utf-8') as json_file:
        tf_data = json.load(json_file)

    for it in tf_data:
        it.update({"address_primary": re.sub(r"\W+", " ", it["address_primary"])})
        it.update({"phone_no": re.sub(r"\D+", "", it["telephone"])})



    # # Dictionary containing info for
    # centers_info = dict([(center["organisation_name"],
    #                       {"telephone": center["telephone"], "email": center["email"],
    #                        "website": center["website"], "address": center["address_primary"]}
    #                       ) for center in tf_data])
    #
    # centers_coords =

    countries = list(
        filter(lambda elm: elm!=('',''),
               zip(*[sorted(set(map(lambda el: el["country_name"], tf_data)))]*2))
    )

    # form = TestFinderForm(countries)


    # if request.method == "GET":
    loc_data["init_country"] = list(filter(lambda el: el["country_key"] == lang_to_flag(lang),
                                   tf_data)).pop().get("country_name")
    hiv_test = False
    hepc_test = False
    sti_test = False


    flds_lbl_val = {"country": (loc_data["country_lbl"], loc_data["init_country"]),
                    "testing_hiv": (loc_data["hiv_test_lbl"], hiv_test),
                    "testing_hepc": (loc_data["hepc_test_lbl"], hepc_test),
                    "testing_sti": (loc_data["sti_test_lbl"], sti_test)
                    }

    form = TestFinderForm(countries, flds_lbl_val)

    # if form.validate_on_submit():
    #     selected_country = form.country.data
    #     hiv_test = form.hiv_test.data
    #     hepc_test = form.hepc_test.data
    #     sti_test = form.sti_test.data
    #
    #     flds_lbl_val = {"country": (loc_data["country_lbl"], selected_country),
    #                     "hiv_test": (loc_data["hiv_test_lbl"], hiv_test),
    #                     "hepc_test": (loc_data["hepc_test_lbl"], hepc_test),
    #                     "sti_test": (loc_data["sti_test_lbl"], sti_test)
    #                     }

    loc_data["key"] = app.config["GOOGLE_API_KEY"]
    country_coords, zoom = country_location(loc_data["init_country"], loc_data["key"])

    loc_data["lat"], loc_data["lng"] = country_coords.get("lat"), country_coords.get("lng")
    loc_data["zoom"] = zoom

    return render_template("test_finder.html", loc_data=loc_data, form=form, tf_data=tf_data, str_centers=str(tf_data))


@app.route("/survey", methods = ['POST', 'GET'])
def survey():
    lang = request.args.get('lang') or "en"
    # json_params = {"language": lang}
    url = "/".join([backend_server, "survey", lang])

    if not session.get("access_token"):
        get_url = "/".join([backend_server, "create_token"])
        response = requests.get(get_url)
        if response.status_code == 200:
            json_data = response.json()
            session["access_token"] = json_data.get("access_token")
            session["refresh_token"] = json_data.get("refresh_token")
        else:
            return render_template("500.html")

    headers = {"Content-Type": "application/json",
               "Accept": "application/json",
               "Authorization": "Bearer {}".format(
                   session.get("access_token", None)
               ) if session.get("access_token", None) else ""
               }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.text)
    else:
        # if response.status_code == 401:
        #     if session.get("refresh_code"):
        data={}

    form_errors, _ = translated_content(request, "form_errors/form_errors")

    form = SurveyForm(data)

    if form.validate_on_submit():
        submit_data = {}
        #

        submit_data["answers"] = [
            [int(form.useful.data)], list(map(int, form.interesting_components.data)),
            [int(form.take_action.data)], list(map(int, form.which_action.data or [-1])),
            [int(form.use_again.data)], [int(form.gender.data)],
            [int(form.age_category.data)], list(map(int, form.evaluations.data)),
            [form.comment.data]]

        # submit_data["answers"] = [([fval] if type(
        #     fval)==int else list(map(int, fval))) for fname, fval in form.data.items() if fname!= "csrf_token"]

        # submit_data["token"] = session.get("token", None)
        submit_data["language"] = lang

        post_url = "/".join([backend_server, "survey_answers"])
        response = requests.post(post_url, json=submit_data, headers=headers)


        if response.status_code == 200:
            data = response.json()
            assure_msg = data["text"] or ""
            # session["token"] = data["token"]

        #     data["link-colors"] = ["btn-danger", "btn-dark", "btn-primary"]
        #     data["btn-colors"] = button_colors[:len(data["data"]["options"])]

        # If not authorized, most probably access token expired, refresh token
        elif response.status_code == 401:
            if session.get("refresh_token"):
                refresh_url = "/".join([backend_server, "refresh_token"])

                ref_headers = {"Content-Type": "application/json",
                               "Accept": "application/json",
                               "Authorization": "Bearer {}".format(
                                   session.get("refresh_token", None)
                               ) if session.get("refresh_token", None) else ""
                               }
                refresh_resp = requests.get(refresh_url, headers=ref_headers)

                if refresh_resp.status_code == 200:
                    refresh_json = refresh_resp.json()
                    session["access_token"] = refresh_json.get("access_token")
                    headers = {"Content-Type": "application/json",
                               "Accept": "application/json",
                               "Authorization": "Bearer {}".format(
                                   session.get("access_token", None)
                               ) if session.get("access_token", None) else ""
                               }
                    resp = requests.post(post_url, json=submit_data, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        assure_msg = data["text"] or ""
                    else:
                        return render_template("{}.html".format(resp.status_code))
        else:
            return render_template("{}.html".format(response.status_code))

        return redirect(url_for("assure", assure_msg=assure_msg))

    # with open("tr/form_errors/form_errors_en.json", encoding='utf-8') as fp:
    #     en_form_errors = json.load(fp)
    #
    # form_errors = dict([(en_form_errors[error_type], error_msg) for error_type, error_msg in form_errors.items()])
    # print(form_errors)
    #
    # print(form.errors.items())

    return render_template('survey_modal.html', form=form, form_errors=form_errors)


@app.route("/assure", methods = ['POST', 'GET'])
def assure():
    loc_data = {}
    loc_data["modal_body"] = request.args.get('assure_msg')
    # loc_data, lang = translated_content(request, "survey/assure")
    return render_template('modal_assure.html', loc_data=loc_data)


@app.route("/pn")
def partner_notification():
    lang = request.args.get('lang') or "en"

    loc_data, _ = translated_content(request, "pn/pn")  # Change with service

    # url = "/".join([backend_server, "pn", lang])
    #
    # response = requests.get(url)
    # if response.status_code == 200:
    #     data = json.loads(response.text)
    # else:
    #     data = {}

    with open("tr/pn/pn_faq_{}.html".format(lang), encoding='utf-8') as html_fp:
        data = html_fp.read()

    return render_template('partner_notification.html',
                           enter_pass_title=loc_data["passcode_form"].get("enter_pass_title", ""),
                           notify_btn_label= loc_data.get("notify_btn_label"),
                           faq_txt=data)


@app.route("/passvalidation", methods=['POST', 'GET'])
def passcode_validation():
    lang = request.args.get('lang') or "en"

    loc_data, _ = translated_content(request, "pn/pn")  # Change with service
    loc_data = loc_data.get("passcode_form", None)

    form_errors, _ = translated_content(request, "form_errors/form_errors")
    form = PasscodeForm()
    wrong_pass_error = ""

    if form.validate_on_submit():
        post_url = "/".join([pn_services_server, "auth"])
        passcode = "".join(form.passcode_flds.data)
        response = requests.post(post_url, json={"passcode": passcode})

        if response.status_code == 200:
            data = response.json()
            access_token = data["access_token"] or ""
            session["access_token"] = access_token
            session["passcode"] = passcode
            return redirect(url_for("send_msg", lang=lang))

        elif response.status_code == 401:
            #  In case of wrong passcode return error
            wrong_pass_error = loc_data.get("wrong_pass_error", "")
        elif response.status_code == 404:
            return render_template("404.html")
        elif response.status_code == 405:
            return render_template("405.html")
        elif response.status_code == 500:
            return render_template("500.html")

    return render_template('passvalidation_modal.html', form=form,
                           loc_data=loc_data, wrong_pass_error=wrong_pass_error, form_errors=form_errors)


@app.route("/sendmsg", methods=['POST', 'GET'])
def send_msg():
    lang = request.args.get('lang') or "en"
    # access_token = session["access_token"]

    loc_data, _ = translated_content(request, "pn/pn")  # Change with service
    loc_data = loc_data.get("send_msg_form", None)

    # Message template, change link placeholders with the actual links
    msg_template = loc_data.get("msg_template")
    loc_data["msg_template"] = msg_template.replace(
        "[integrateja_link]", loc_data.get("integrateja_link")).replace(
        "[testfinder_link]", loc_data.get("testfinder_link")) if msg_template else ""

    form_errors, _ = translated_content(request, "form_errors/form_errors")
    form = SendMsgForm()
    form.msg.data = loc_data["msg_template"]


    if form.validate_on_submit():
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            # "Authorization": "Bearer {}".format(base64.b64encode(access_token) ) if access_token else "",
            "Authorization": "Bearer {}".format(session.get("access_token") or ""),
        }
        post_url = "/".join([pn_services_server, "sendmsg"])

        phone_nums = [phone.replace("-","").replace(" ","") for phone in form.phone_numbers.data if phone]

        response = requests.post(
            post_url, json={"passcode": session.get("passcode"),
                       "phone_numbers": phone_nums,
                       "msg": form.msg.data}, headers=headers)


        loc_data["modal_body_extra"] = ""

        if response.status_code == 401:
            #  If access_token has expired, renew access_token
            return redirect(url_for("passcode_validation", lang=lang))
        elif response.status_code == 200:
            data = response.json()
            successful_sends =  data.pop("data")
            unsuccessful_sends = list(set(phone_nums) - set(successful_sends))

            if data and next(iter(data.get("ret"))) == "200":
                loc_data["modal_body"] = "{}: {}".format(
                    loc_data["send_success"], ",".join(successful_sends)) if successful_sends else ""

                # In case there are numbers that message could not be sent to
                loc_data["modal_body_extra"] = "{}: {}".format(
                    loc_data["send_failure"], ",".join(unsuccessful_sends)) if unsuccessful_sends else ""

            else:
                loc_data["modal_body"] = "{}: {}".format(loc_data["send_failure"],
                                                         ",".join(phone_nums))

        elif response.status_code == 404:
            return render_template("404.html")
        elif response.status_code == 405:
            return render_template("405.html")
        elif response.status_code == 500:
            return render_template("500.html")

        return render_template('modal_assure.html',
                               loc_data=loc_data )

    return render_template('send_msg.html', form=form,
                           loc_data=loc_data, form_errors=form_errors)


@app.route("/about")
def about():
    loc_data, lang = translated_content(request, "about/about")
    return render_template("about.html", loc_data=loc_data)


@app.route("/contact")
def contact():
    loc_data, lang = translated_content(request, "contact/contact")
    return render_template("contact.html", loc_data=loc_data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port = 3000, debug = True)
