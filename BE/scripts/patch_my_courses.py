from pathlib import Path

p = Path(r"c:\Users\Admin\AI-Learning-Platform\FE\src\pages\enrollment\MyCoursesPage.jsx")
text = p.read_text(encoding="utf-8")

old_close = (
    "                      )}\n"
    "                    </motion.div>\n"
    "                  </motion.div>\n"
    "                </motion.div>"
)
new_close = (
    "                      )}\n"
    "                    </div>\n"
    "                  </div>\n"
    "                </motion.div>"
)
if old_close in text:
    text = text.replace(old_close, new_close, 1)

needle = (
    '                    <div className="mc-card__actions">\n'
    "                      {enrollment.status === 'in-progress' && ("
)
repl = (
    '                    <motion.div className="mc-card__actions">\n'
    "                      <Button\n"
    '                        variant="outline"\n'
    '                        size="sm"\n'
    "                        onClick={() => navigate(`/dashboard/enrollment/${eid}`)}\n"
    "                      >\n"
    "                        Chi tiết đăng ký\n"
    "                      </Button>\n"
    "                      {enrollment.status === 'in-progress' && ("
)
repl = (
    '                    <div className="mc-card__actions">\n'
    "                      <Button\n"
    '                        variant="outline"\n'
    '                        size="sm"\n'
    "                        onClick={() => navigate(`/dashboard/enrollment/${eid}`)}\n"
    "                      >\n"
    "                        Chi tiết đăng ký\n"
    "                      </Button>\n"
    "                      {enrollment.status === 'in-progress' && ("
)

if "Chi tiết đăng ký" not in text and needle in text:
    text = text.replace(needle, repl, 1)

p.write_text(text, encoding="utf-8")
print("done")
