import datetime
import textwrap
import time

import bs4
import pytest

from web.commands import schedule

SCHEDULE_HTML = textwrap.dedent(
    """
    <h2>Staff schedule for week beginning 2020-05-25</h2>
    </td>
    <td>
    <table cellspacing=0 cellpadding=2 class="calmonth">
    <tr class="dark">
    <td style="text-align:left"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?week=737516">&laquo;</a></td>
    <td colspan="5" style="text-align:center;">May 2020</td>
    <td style="text-align:right"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?week=737577">&raquo;</a></td>
    </tr>
    <tr class="light"><th>S</th><th>M</b></th><th>T</b></th><th>W</b></th><th>T</b></th><th>F</b></th><th>S</b></th></tr>
    <tr class="dark">
    <td width="14%"></td>
    <td width="14%"></td>
    <td width="14%"></td>
    <td width="14%"></td>
    <td width="14%"></td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737546">1</td>
    <td width="14%">2</td>
    </tr>
    <tr class="light">
    <td width="14%">3</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737549">4</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737550">5</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737551">6</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737552">7</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737553">8</td>
    <td width="14%">9</td>
    </tr>
    <tr class="dark">
    <td width="14%">10</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737556">11</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737557">12</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737558">13</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737559">14</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737560">15</td>
    <td width="14%">16</td>
    </tr>
    <tr class="light">
    <td width="14%">17</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737563">18</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737564">19</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737565">20</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737566">21</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737567">22</td>
    <td width="14%">23</td>
    </tr>
    <tr class="dark">
    <td width="14%">24</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737570">25</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737571">26</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737572">27</td>
    <td width="14%" style="font-weight:bold;background-color:#4444FF"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737573" style="color:white;">28</td>
    <td width="14%"><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737574">29</td>
    <td width="14%">30</td>
    </tr>
    <tr class="light">
    <td width="14%">31</td>
    <td width="14%"></td>
    <td width="14%"></td>
    <td width="14%"></td>
    <td width="14%"></td>
    <td width="14%"></td>
    </tr>
    </table>
    </td>
    </tr>
    </table>
    <b>Rust Duty:</b> Ian Ross and Mark Coatsworth<br>

    <br>
    <table>
    <tr border=0>
    <td align=left>
    <a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?week=737563"><img border=0 src="back.gif"></a>
    </td>
    <td colspan=4 align=center>
    <a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl">Home</a>
    </td>
    <td align=right>
    <a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?week=737577"><img border=0 src="forward.gif"></a>
    </td>
    </tr>
    <tr class=dark>
    <td></td>
    <td><b><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737570">Monday<br>2020-05-25</a></b></td>
    <td><b><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737571">Tuesday<br>2020-05-26</a></b></td>
    <td><b><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737572">Wednesday<br>2020-05-27</a></b></td>
    <td><b><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737573">Thursday<br>2020-05-28</a></b></td>
    <td><b><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?day=737574">Friday<br>2020-05-29</a></b></td>
    </tr>
    <tr class=light>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=moate">Aaron Moate</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    </tr>
    <tr class=dark>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=blin">Brian Lin</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    </tr>
    <tr class=light>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=edquist">Carl Edquist</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    11:00am to 08:00pm
    </td>
    <td>Office<br>
    11:00am to 08:00pm
    </td>
    <td>Office<br>
    11:00am to 08:00pm
    </td>
    <td>Office<br>
    11:00am to 08:00pm
    </td>
    </tr>
    <tr class=dark>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=ckoch5">Christina Koch</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    </tr>
    <tr class=light>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=gthain">Greg Thain</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    <td>Office<br>
    08:30am to 05:30pm
    </td>
    </tr>
    <tr class=dark>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=iross">Ian Ross</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    08:15am to 04:45pm
    </td>
    <td>Office<br>
    08:15am to 04:45pm
    </td>
    <td>Office<br>
    08:15am to 04:45pm
    </td>
    <td>Office<br>
    08:15am to 04:45pm
    </td>
    </tr>
    <tr class=light>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=jfrey">Jaime Frey</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    08:30am to 04:30pm
    </td>
    <td>Office<br>
    08:30am to 04:30pm
    </td>
    <td>Office<br>
    08:30am to 04:30pm
    </td>
    <td>Office<br>
    08:30am to 04:30pm
    </td>
    </tr>
    <tr class=dark>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=jpatton">Jason Patton</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office (Home)<br>
    08:15am to 05:00pm
    </td>
    <td>Office (Home)<br>
    08:15am to 05:00pm
    </td>
    <td>Office (Home)<br>
    08:15am to 05:00pm
    </td>
    <td>Office (Home)<br>
    08:15am to 05:00pm
    </td>
    </tr>
    <tr class=light>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=jmvera">Jess Vera</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    08:45am to 05:15pm
    </td>
    <td>Office<br>
    08:45am to 05:15pm
    </td>
    <td>Office<br>
    08:45am to 05:15pm
    </td>
    <td>Office<br>
    08:45am to 05:15pm
    </td>
    </tr>
    <tr class=dark>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=kupsch">Jim Kupsch</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    08:00am to 04:00pm
    </td>
    <td>Office<br>
    08:00am to 04:00pm
    </td>
    <td>Office<br>
    08:00am to 04:00pm
    </td>
    <td>Office<br>
    08:00am to 04:00pm
    </td>
    </tr>
    <tr class=light>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=johnkn">John (TJ) Knoeller</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td><span class="away">Furlough</span> (1)<br>
    </td>
    <td>Office<br>
    09:30am to 05:30pm
    </td>
    <td>Office<br>
    09:30am to 05:30pm
    </td>
    <td>Office<br>
    09:30am to 05:30pm
    </td>
    </tr>
    <tr class=dark>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=karpel">Joshua Karpel</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    </tr>
    <tr class=light>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=lmichael">Lauren Michael</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td><span class="away">Off:8</span> (4/5 week make-up, in Madison)<br>
    </td>
    <td><span class="away">Off:8</span> (4/5 week make-up, in Madison)<br>
    </td>
    <td><span class="away">Off:8</span> (4/11-12 make-up, in Madison)<br>
    </td>
    <td><span class="away">Off:8</span> (4/13 week make-up, in Madison)<br>
    </td>
    </tr>
    <tr class=dark>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=coatsworth">Mark Coatsworth</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td><span class="away">Vacation</span><br>
    </td>
    <td>Office<br>
    09:30am to 05:30pm
    </td>
    <td>Office<br>
    09:30am to 05:30pm
    </td>
    <td>Office<br>
    09:30am to 05:30pm
    </td>
    </tr>
    <tr class=light>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=matyas">Matyas Selmeci</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office (WFH)<br>
    09:00am to 05:30pm
    </td>
    <td>Office (WFH)<br>
    09:00am to 05:30pm
    </td>
    <td>Office (WFH)<br>
    09:00am to 05:30pm
    </td>
    <td>Office (WFH)<br>
    09:00am to 05:30pm
    </td>
    </tr>
    <tr class=dark>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=miron">Miron Livny</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    05:00am to 11:59pm
    </td>
    <td>Office<br>
    05:00am to 11:59pm
    </td>
    <td>Office<br>
    05:00am to 11:59pm
    </td>
    <td>Office<br>
    05:00am to 11:59pm
    </td>
    </tr>
    <tr class=light>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=cat">Tim Cartwright</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    </tr>
    <tr class=dark>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tjslauson">Tim Slauson</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    <td>Office<br>
    09:00am to 05:00pm
    </td>
    </tr>
    <tr class=light>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tim">Tim Theisen</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office (Home)<br>
    08:00am to 05:30pm
    </td>
    <td>Office<br>
    08:00am to 03:00pm
    </td>
    <td>Office (Home)<br>
    08:00am to 05:30pm
    </td>
    <td>Office (Home)<br>
    08:00am to 05:30pm
    </td>
    </tr>
    <tr class=dark>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tlmiller">Todd Miller</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    10:00am to 06:00pm
    </td>
    <td>Office<br>
    10:00am to 06:00pm
    </td>
    <td>Office<br>
    10:00am to 06:00pm
    </td>
    <td>Office<br>
    10:00am to 06:00pm
    </td>
    </tr>
    <tr class=light>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tannenba">Todd Tannenbaum</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td><span class="away">Vacation</span><br>
    </td>
    <td>Office<br>
    09:45am to 05:45pm
    </td>
    <td><span class="away">Furlough</span><br>
    </td>
    <td><span class="away">Furlough</span><br>
    </td>
    </tr>
    <tr class=dark>
    <td><a href="https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=zmiller">Zach Miller</a></td>
    <td><span class="away">Holiday</span> (Memorial Day)<br>
    </td>
    <td>Office<br>
    09:30am to 05:30pm
    </td>
    <td>Office<br>
    09:30am to 05:30pm
    </td>
    <td>Office<br>
    09:30am to 05:30pm
    </td>
    <td>Office<br>
    09:30am to 05:30pm
    </td>
    </tr>
    </table>
    """
).strip()


@pytest.fixture
def soup():
    return bs4.BeautifulSoup(SCHEDULE_HTML, "html.parser")


@pytest.fixture
def sch():
    return schedule.ScheduleCommandHandler()


@pytest.mark.parametrize(
    "users, dayofweek, expected",
    [
        (
            [],
            0,
            {
                "Holiday (Memorial Day)": [
                    (
                        "Aaron Moate",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=moate",
                        None,
                    ),
                    (
                        "Brian Lin",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=blin",
                        None,
                    ),
                    (
                        "Carl Edquist",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=edquist",
                        None,
                    ),
                    (
                        "Christina Koch",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=ckoch5",
                        None,
                    ),
                    (
                        "Greg Thain",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=gthain",
                        None,
                    ),
                    (
                        "Ian Ross",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=iross",
                        None,
                    ),
                    (
                        "Jaime Frey",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=jfrey",
                        None,
                    ),
                    (
                        "Jason Patton",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=jpatton",
                        None,
                    ),
                    (
                        "Jess Vera",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=jmvera",
                        None,
                    ),
                    (
                        "Jim Kupsch",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=kupsch",
                        None,
                    ),
                    (
                        "John (TJ) Knoeller",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=johnkn",
                        None,
                    ),
                    (
                        "Joshua Karpel",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=karpel",
                        None,
                    ),
                    (
                        "Lauren Michael",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=lmichael",
                        None,
                    ),
                    (
                        "Mark Coatsworth",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=coatsworth",
                        None,
                    ),
                    (
                        "Matyas Selmeci",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=matyas",
                        None,
                    ),
                    (
                        "Miron Livny",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=miron",
                        None,
                    ),
                    (
                        "Tim Cartwright",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=cat",
                        None,
                    ),
                    (
                        "Tim Slauson",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tjslauson",
                        None,
                    ),
                    (
                        "Tim Theisen",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tim",
                        None,
                    ),
                    (
                        "Todd Miller",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tlmiller",
                        None,
                    ),
                    (
                        "Todd Tannenbaum",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tannenba",
                        None,
                    ),
                    (
                        "Zach Miller",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=zmiller",
                        None,
                    ),
                ]
            },
        ),
        (
            [],
            2,
            {
                "working": [
                    (
                        "Aaron Moate",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=moate",
                        "09:00am to 05:00pm",
                    ),
                    (
                        "Brian Lin",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=blin",
                        "08:30am to 05:30pm",
                    ),
                    (
                        "Carl Edquist",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=edquist",
                        "11:00am to 08:00pm",
                    ),
                    (
                        "Christina Koch",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=ckoch5",
                        "08:30am to 05:30pm",
                    ),
                    (
                        "Greg Thain",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=gthain",
                        "08:30am to 05:30pm",
                    ),
                    (
                        "Ian Ross",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=iross",
                        "08:15am to 04:45pm",
                    ),
                    (
                        "Jaime Frey",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=jfrey",
                        "08:30am to 04:30pm",
                    ),
                    (
                        "Jason Patton",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=jpatton",
                        "08:15am to 05:00pm",
                    ),
                    (
                        "Jess Vera",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=jmvera",
                        "08:45am to 05:15pm",
                    ),
                    (
                        "Jim Kupsch",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=kupsch",
                        "08:00am to 04:00pm",
                    ),
                    (
                        "John (TJ) Knoeller",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=johnkn",
                        "09:30am to 05:30pm",
                    ),
                    (
                        "Joshua Karpel",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=karpel",
                        "09:00am to 05:00pm",
                    ),
                    (
                        "Mark Coatsworth",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=coatsworth",
                        "09:30am to 05:30pm",
                    ),
                    (
                        "Matyas Selmeci",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=matyas",
                        "09:00am to 05:30pm",
                    ),
                    (
                        "Miron Livny",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=miron",
                        "05:00am to 11:59pm",
                    ),
                    (
                        "Tim Cartwright",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=cat",
                        "09:00am to 05:00pm",
                    ),
                    (
                        "Tim Slauson",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tjslauson",
                        "09:00am to 05:00pm",
                    ),
                    (
                        "Tim Theisen",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tim",
                        "08:00am to 03:00pm",
                    ),
                    (
                        "Todd Miller",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tlmiller",
                        "10:00am to 06:00pm",
                    ),
                    (
                        "Todd Tannenbaum",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tannenba",
                        "09:45am to 05:45pm",
                    ),
                    (
                        "Zach Miller",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=zmiller",
                        "09:30am to 05:30pm",
                    ),
                ],
                "Off:8 (4/5 week make-up, in Madison)": [
                    (
                        "Lauren Michael",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=lmichael",
                        None,
                    )
                ],
            },
        ),
        (
            ["Todd Miller"],
            0,
            {
                "Holiday (Memorial Day)": [
                    (
                        "Todd Miller",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tlmiller",
                        None,
                    )
                ]
            },
        ),
        (
            ["Todd Miller"],
            4,
            {
                "working": [
                    (
                        "Todd Miller",
                        "https://research.cs.wisc.edu/htcondor/developers/schedules/schedules.pl?person=tlmiller",
                        "10:00am to 06:00pm",
                    )
                ]
            },
        ),
    ],
)
def test_get_users_by_status(sch, users, dayofweek, soup, expected):
    print(sch.get_users_by_status(users, dayofweek, soup))
    assert expected == sch.get_users_by_status(users, dayofweek, soup)


@pytest.mark.parametrize(
    "text, dayofweek, expected",
    [
        ("", 1, ["working", "Furlough (1)", "Off:8", "on vacation", "Todd Miller"]),
        ("Todd Miller", 0, ["Todd Miller", "Holiday (Memorial Day)"]),
    ],
)
def test_handle_schedule_end_to_end(mocker, soup, client, text, dayofweek, expected):
    # Intercept the reply, as usual.
    mock_post_message = mocker.patch("web.slack.post_message")

    # We can't intercept web.cached_get_url() as usual because get_soup()
    # expects to be able to find the schedule password.
    mock_get_soup = mocker.patch("web.commands.ScheduleCommandHandler.get_soup")
    mock_get_soup.return_value = soup

    # Likewise, we need to fix which day of the week it is.
    mock_get_dow = mocker.patch("web.commands.ScheduleCommandHandler.get_dayofweek")
    mock_get_dow.return_value = dayofweek

    client.post(
        "/slash/schedule", data=dict(channel_id="1234", user_id="5678", text=text),
    )

    # let the executor run
    time.sleep(0.1)

    assert mock_get_soup.call_count == 1
    assert mock_post_message.call_count == 1

    channel = mock_post_message.call_args[1]["channel"]
    assert channel == "5678"

    msg = mock_post_message.call_args[1]["text"]
    assert all(e in msg for e in expected)
