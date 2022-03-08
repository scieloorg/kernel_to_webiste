from datetime import datetime

import logging
import opac_schema.v1.models as v1_models
import opac_schema.v2.models as v2_models


class DocumentDoesNotExistError(Exception):
    """ To handle not found document.
    """


class RemoteAndLocalFileError(Exception):
    """ To handle file remote-to-local translation errors
    """


def get_journals():
    """
    Get available instances of `opac_schema.v1.models.Journal`
    Returns
    -------
    journals: a list of `opac_schema.v1.models.Journal`
    """
    return v1_models.Journal.objects.all()


def get_article_files_by_pid(pid_v3):
    """
    Get `opac_schema.v2.models.ArticleFiles` according to
    field `pid_v3`
    Parameters
    ----------
    pid_v3: str
    Returns
    -------
    article_files: a list of `opac_schema.v2.models.ArticleFiles`
    """
    return v2_models.ArticleFiles.objects(aid=pid_v3).order_by('-updated')


def get_article_files_by_pid_and_version(pid_v3, version):
    """
    Get `opac_schema.v2.models.ArticleFiles` according to
    fields `pid_v3` and `version`
    Returns
    -------
    article_files: `opac_schema.v2.models.ArticleFiles`
    """
    return v2_models.ArticleFiles.objects.get(aid=pid_v3, version=version)


def get_article_by_pid(pid_v3):
    """
    Get `opac_schema.v1.models.Article` according to
    field `pid_v3`
    Parameters
    ----------
    pid_v3: str
    Returns
    -------
    article: `opac_schema.v1.models.Article`
    """
    try:
        return v1_models.Article.objects.get(aid=pid_v3)
    except v1_models.Article.DoesNotExist:
        raise DocumentDoesNotExistError(
            f'Document {pid_v3} does not exist'
        )


def get_article_uris_and_names(pid_v3):
    """
    Get uri and name of `opac_schema.v1.models.Article.xml`
    and `opac_schema.v1.models.Article.pdfs`
    according to field `pid_v3`
    Parameters
    ----------
    pid_v3: str
    Returns
    -------
    xml_uri_and_name: dict
    renditions_uris_and_names: dict
    """
    renditions_uri_and_names = []

    try:
        article = get_article_by_pid(pid_v3)
    except DocumentDoesNotExistError:
        raise

    xml_uri_and_name = {
        'uri': article.xml,
        'name': f'{pid_v3}.xml',
    }

    for rendition in article.pdfs:
        renditions_uri_and_names.append({
            'uri': rendition['url'],
            'name': rendition['filename'],
        })

    return xml_uri_and_name, renditions_uri_and_names


def generate_article_files_version_number(pid_v3):
    """
    Get `opac_schema.v2.models.ArticleFiles.version`
    according to field `pid_v3`
    Parameters
    ----------
    pid_v3: str
    Returns
    -------
    next_version: int
    """
    current_version = get_article_files_by_pid(pid_v3).count() or 0
    next_version = current_version + 1
    return next_version


def add_article_files(pid_v3, package_uris_and_names):
    """
    Register an instance of `opac_schema.v2.models.ArticleFiles`
    Parameters
    ----------
    pid_v3: str
    package_uris_and_names: dict
    Returns
    -------
    article_files: `opac_schena.v2.models.ArticleFiles`
    """
    article_files = v2_models.ArticleFiles()
    article_files.aid = pid_v3
    article_files.version = generate_article_files_version_number(pid_v3)
    article_files.scielo_pids = {'v3': pid_v3}
    set_article_files_paths(article_files, package_uris_and_names)
    article_files.save()

    return article_files


def set_article_files_paths(article_files, package_uris_and_names):
    """
    Update `opac_schema.v2.models.ArticleFiles.xml`,
    `opac_schema.v2.models.ArticleFiles.renditions`
    and `opac_schema.v2.models.ArticleFiles.assets`
    with `packages_uris_and_names`
    Parameters
    ----------
    article_files: opac_schema.v2.models.ArticleFiles
    packages_uris_and_names: dict
    """
    article_files.xml = create_remote_and_local_file(
        package_uris_and_names['xml']['uri'],
        package_uris_and_names['xml']['name']
    )

    article_files.file = create_remote_and_local_file(
        package_uris_and_names['file']['uri'],
        package_uris_and_names['file']['name']
    )

    assets = []
    for item in package_uris_and_names["assets"]:
        assets.append(
            create_remote_and_local_file(
                item['uri'],
                item['name']
            )
        )
    article_files.assets = assets

    renditions = []
    for item in package_uris_and_names["renditions"]:
        renditions.append(
            create_remote_and_local_file(
                item.get('uri') or item.get('url'),
                item['name']
            )
        )
    article_files.renditions = renditions


def update_article(pid, xml_sps, xml_uri, renditions_uris_and_names, is_public=True, issue_id=None, article_order=None, other_pids=[]):
    """
    Update `opac_schema.v1.models.Article`
    with `sps_package`, `xml_uri`, `renditions_uris_and_names`,
    `is_public`, `issue_id`, `article_order` and `other_pids`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    sps_package: packtools.sps.models.sps_package.SPS_Package
    xml_uri: dict
    renditions_uris_and_names: list
    is_public: boolean
    issue_id: int
    article_order: int
    other_pids: list
    """
    article = get_article_by_pid(pid)

    set_renditions(article, renditions_uris_and_names)
    set_xml_uri(article, xml_uri)
    set_issue_data(article, issue_id)
    set_order(article, xml_sps, article_order)
    set_ids(article, xml_sps)
    set_is_public(article, is_public=is_public)
    set_languages(article, xml_sps)
    set_article_abstracts(article, xml_sps)
    set_article_authors(article, xml_sps)
    set_article_pages(article, xml_sps)
    set_article_publication_date(article, xml_sps)
    set_article_sections(article, xml_sps)
    set_article_titles(article, xml_sps)
    set_article_type(article, xml_sps)
    add_other_pids(article, other_pids)

    set_updated(article)

    article.save()


def set_renditions(article, renditions):
    """
    Update `opac_schema.v1.models.Article.pdfs`
    with `renditions`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    renditions_uris_and_names: list
    """
    _normalize_renditions(renditions)
    article.pdfs = renditions


def _normalize_renditions(renditions):
    """
    Normalize renditions data according to `article.pdfs` keys
    Parameters
    ----------
    renditions: dict
    """
    for r in renditions:
        if 'uri' in r:
            r['url'] = r['uri']
            del r['uri']


def set_xml_uri(article, xml_uri):
    """
    Update `opac_schema.v1.models.Article.xml`
    with `xml_url`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    xml_uri: dict
    """
    article.xml = xml_uri


def set_updated(article):
    """
    Update `opac_schema.v1.models.Article.updated`
    with `datetime.utcnow()`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    """
    article.updated = datetime.utcnow()


def add_other_pids(article, other_pids):
    """
    Update `opac_schema.v1.models.Article.scielo_pids`
    with `other_pids`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    other_pids: list
    """
    if other_pids:
        article.scielo_pids.update(
            {
                "other":
                list(set(list(article.scielo_pids.get("other") or []) +
                     list(other_pids)))
            }
        )


def set_order(article, sps_package, article_order):
    """
    Update `opac_schema.v1.models.Article.order`
    with `article_order`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    article_order: int
    """
    article.order = get_order(sps_package, article_order)


def set_issue_data(article, issue_id):
    """
    Update `opac_schema.v1.models.Article.issue`
    with `v1_models.Issue`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    issue_id: int
    """
    if issue_id is None:
        issue_id = article.issue._id

    if article.issue is not None and article.issue.number == "ahead":
        if article.aop_url_segs is None:
            url_segs = {
                "url_seg_article": article.url_segment,
                "url_seg_issue": article.issue.url_segment,
            }
            article.aop_url_segs = v1_models.AOPUrlSegments(**url_segs)

    # Issue vinculada
    issue = v1_models.Issue.objects.get(_id=issue_id)

    logging.info("ISSUE %s" % str(issue))
    logging.info("ARTICLE.ISSUE %s" % str(article.issue))
    logging.info("ARTICLE.AOP_PID %s" % str(article.aop_pid))
    logging.info("ARTICLE.PID %s" % str(article.pid))

    article.issue = issue
    article.journal = issue.journal


def set_is_public(article, is_public=True):
    """
    Update `opac_schema.v1.models.Article.is_public`
    with `is_public`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    is_public: boolean
    """
    article.is_public = is_public


def set_ids(article, sps_package):
    """
    Update `opac_schema.v1.models.Article` identifiers
    with `sps_package` identifiers
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    sps_package: packtools.sps.models.sps_package.SPS_Package
    """
    article._id = sps_package.scielo_pid_v3
    article.aid = sps_package.scielo_pid_v3
    article.scielo_pids = sps_package.article_ids
    article.aop_pid = sps_package.aop_pid
    article.pid = sps_package.scielo_pid_v2
    article.doi = sps_package.doi


def set_article_type(article, sps_package):
    """
    Update `opac_schema.v1.models.Article.type`
    with `sps_package.article_type`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    sps_package: packtools.sps.models.sps_package.SPS_Package
    """
    article.type = sps_package.article_type


def set_languages(article, sps_package):
    """
    Update `opac_schema.v1.models.Article.original_language`,
    `opac_schema_v1.models.Article.languages`
    and `opac_schema_v1.models.Article.htmls`
    with `sps_package.lang`
    and `sps_package.languages`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    sps_package: packtools.sps.models.sps_package.SPS_Package
    """
    article.original_language = sps_package.lang
    article.languages = sps_package.languages
    article.htmls = [{"lang": lang} for lang in sps_package.languages]


def set_article_titles(article, sps_package):
    """
    Update `opac_schema.v1.models.Article.title`
    and translated_titles
    `opac_schema_v1.models.Article.languages`
    and `opac_schema_v1.models.Article.translated_titles`
    with `sps_package.article_title`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    sps_package: packtools.sps.models.sps_package.SPS_Package
    """
    article.title = sps_package.article_title
    langs_and_titles = {
        lang: title
        for lang, title in sps_package.article_titles.items()
        if lang != sps_package.lang
    }
    set_translate_titles(article, langs_and_titles)


def set_article_sections(article, sps_package):
    """
    Update `opac_schema.v1.models.Article.section`
    and `opac_schema_v1.models.Article.trans_sections`
    with `sps_package.subject`
    and `sps_package.subjects`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    sps_package: packtools.sps.models.sps_package.SPS_Package
    """
    article.section = sps_package.subject
    set_translated_sections(article, sps_package.subjects)


def set_article_abstracts(article, sps_package):
    """
    Update `opac_schema.v1.models.Article.abstract`
    and `opac_schema.v1.models.Article.keywords`
    with `sps_package.abstracts`
    and `sps_package.keywords`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    sps_package: packtools.sps.models.sps_package.SPS_Package
    """
    article.abstract = sps_package.abstract
    set_abstracts(article, sps_package.abstracts)
    set_keywords(article, sps_package.keywords_groups)


def set_article_publication_date(article, sps_package):
    """
    Update `opac_schema.v1.models.Article.publication_date`
    with `sps_package.document_pubdate`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    sps_package: packtools.sps.models.sps_package.SPS_Package
    """
    article.publication_date = "-".join(sps_package.document_pubdate)


def set_article_pages(article, sps_package):
    """
    Update `opac_schema.v1.models.Article` elocation,
    fpage, fpage_sequence and lpage
    with sps_package
    with `sps_package`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    sps_package: packtools.sps.models.sps_package.SPS_Package
    """
    article.elocation = sps_package.elocation_id
    article.fpage = sps_package.fpage
    article.fpage_sequence = sps_package.fpage_seq
    article.lpage = sps_package.lpage


def set_article_authors(article, sps_package):
    """
    Update `opac_schema.v1.models.Article.authors`
    with `sps_package.authors`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    sps_package: packtools.sps.models.sps_package.SPS_Package
    """
    set_authors(article, sps_package.authors)
    set_authors_meta(article, sps_package.authors)


def set_authors(article, authors):
    """
    Update `opac_schema.v1.models.Article.authors`
    with `authors`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    authors: dict which keys are ("surname", "given_names")
    """
    article.authors = [
        f'{a.get("surname")}, {a.get("given_names")}'
        for a in authors
    ]


def set_authors_meta(article, authors):
    """
    Update `opac_schema.v1.models.Article.authors_meta`
    with `authors`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    authors: dict which keys are (
        "surname", "given_names", "orcid", "affiliation", "suffix",
    )
    """
    _authors = []
    for a in authors:
        if not a.get("orcid") and not a.get("affiliation"):
            continue
        author = {}
        if a.get("orcid"):
            author["orcid"] = a.get("orcid")
        if a.get("aff"):
            author["affiliation"] = a.get("aff")
        if a.get("prefix"):
            author["name"] = (
                f'{a.get("surname")} {a.get("prefix")}, {a.get("given_names")}'
            )
        else:
            author["name"] = (
                f'{a.get("surname")}, {a.get("given_names")}'
            )
        _authors.append(v1_models.AuthorMeta(**author))
    article.authors_meta = _authors


def set_translate_titles(article, langs_and_titles):
    """
    Update `opac_schema.v1.models.Article.translated_titles`
    with `langs_and_titles`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    langs_and_titles: dict
    """
    translated_titles = []
    for lang, title in langs_and_titles.items():
        translated_titles.append(
            v1_models.TranslatedTitle(
                **{
                    "name": title,
                    "language": lang,
                }
            )
        )
    article.translated_titles = translated_titles


def set_translated_sections(article, langs_and_sections):
    """
    Update `opac_schema.v1.models.Article.trans_sections`
    with `langs_and_sections`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    langs_and_sections: dict
    """
    if not langs_and_sections:
        # documento não tem seção de sumário
        return
    sections = []
    for lang, section in langs_and_sections.items():
        sections.append(
            v1_models.TranslatedSection(
                **{
                    "name": section,
                    "language": lang,
                }
            )
        )
    article.trans_sections = sections


def set_abstracts(article, langs_and_abstracts):
    """
    Update `opac_schema.v1.models.Article.abstracts` with `langs_and_abstracts`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    langs_and_abstracts: dict
    """
    abstracts = []
    for lang, abstr in langs_and_abstracts.items():
        abstracts.append(
            v1_models.Abstract(
                **{
                    "text": abstr,
                    "language": lang,
                }
            )
        )
    article.abstracts = abstracts
    article.abstract_languages = list(langs_and_abstracts.keys())


def set_keywords(article, langs_and_keywords):
    """
    Update `opac_schema.v1.models.Article.keywords` with `langs_and_keywords`
    Parameters
    ----------
    article: opac_schema.v1.models.Article
    langs_and_keywords: dict
    """
    keywords = []
    for lang, kwds in langs_and_keywords.items():
        keywords.append(
            v1_models.ArticleKeyword(
                **{
                    "keywords": kwds,
                    "language": lang,
                }
            )
        )
    article.keywords = keywords


def create_remote_and_local_file(remote, local, annotation=None):
    """
    Get an instance of `opac_schema.v2.models.RemoteAndLocalFile`
    Parameters
    ----------
    remote: str
    local: str
    annotation: str
    Returns
    -------
    file: opac_schema.v2.models.RemoteAndLocalFile
    """
    try:
        file = {}
        if local:
            file["name"] = local
        if remote:
            file["uri"] = remote
        if annotation:
            file["annotation"] = annotation
        return v2_models.RemoteAndLocalFile(**file)
    except Exception as e:
        raise RemoteAndLocalFileError(
            "Unable to create RemoteAndLocalFile(%s, %s): %s" %
            (remote, local, e)
        )


def get_order(sps_package, article_order):
    """
    Get `opac_schema.v1.models.Article.article_order`
    Parameters
    ----------
    sps_package: packtools.sps.models.sps_package.SPS_Package
    article_order: int
    """
    try:
        return int(article_order)
    except (ValueError, TypeError):
        order_err_msg = (
            "'{}' is not a valid value for "
            "'article.order'".format(article_order)
        )
        logging.info(
            "{}. It was set '{} (the last 5 digits of PID v2)' to "
            "'article.order'".format(order_err_msg, sps_package.order))
        return sps_package.order


def add_received_package(_id, uri, name, annotation=None):
    """
    Register an instance of `opac_schema.v2.models.ReceivedPackage`
    Parameters
    ----------
    _id: str
    uri: str
    name: str
    Returns
    -------
    received_package: `opac_schena.v2.models.ReceivedPackage`
    """
    rp = v2_models.ReceivedPackage()
    rp._id = _id
    rp.file = create_remote_and_local_file(uri, name, annotation)
    rp.updated = datetime.utcnow()
    rp.save()

    return rp
