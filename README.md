## Repositórios de scripts diversos

### download.sh
Script genérico para download paralelo de arquivos usando wget. Basta prover uma lista de urls de arquivos.

```sh
 $ download.sh <url_list_file>

```

### count_objects_into_fits.py
Script para contar objetos (linhas) em arquivos .fits

```sh

source /mnt/eups/linea_eups.sh
setup pyfits 3.4+0

cd /dir/onde/estao/os/fits
python count_objects_into_fits.py

```

### rsync parallel
Script que executa rsync em paralelo

OBS: definir os paths nas variáveis `SRCDIR` e `DESTDIR`, a quantidade de threads definir na variável `THREADS`.

```sh
./rsync_parallel.sh

```
